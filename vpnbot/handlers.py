import asyncio
import logging
import os
from typing import Optional, Dict, Any

import aiohttp
import telegram
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from dotenv import load_dotenv

from vpnbot.utils import save_payment_to_db, activate_subscription, notify_admin, get_tariff_by_id

load_dotenv('.env')

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MINI_APP_URL = os.getenv("MINI_APP_URL", "")
VPN_API_URL = os.getenv("VPN_API_URL", "")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")


async def _handle_edit_failure(update: Update, context: CallbackContext) -> None:
    logger.warning("_handle_edit_failure is running")
    if not update.callback_query or not update.callback_query.message:
        return
    try:
        await update.callback_query.message.reply_text(
            "⚠️ Failed to update message. Please try again."
        )
    except Exception as e:
        logger.error(f"Error in _handle_edit_failure: {e}")


async def get_user(user_id: int, timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Retrieve user data from Django API server."""
    url = f"{VPN_API_URL}/subscription/{user_id}"
    params = {"user_id": user_id}

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                response.raise_for_status()
                return None
    except asyncio.TimeoutError:
        raise aiohttp.ClientError(f"Request timed out after {timeout} seconds")
    except aiohttp.ClientError as e:
        raise aiohttp.ClientError(f"Failed to fetch user: {str(e)}")


def format_user_data(data: Dict[str, Any]) -> str:
    """Format user data for display."""
    traffic_used = float(data.get("trafficUsed", 0)) or 0
    traffic_limit = float(data.get("trafficLimit", 1)) or 1  # avoid division by zero
    traffic_percent = (
        min(100, (traffic_used / traffic_limit) * 100) if traffic_limit else 0
    )

    progress_blocks = int(traffic_percent / 10)
    progress_bar = "[" + "■" * progress_blocks + "□" * (10 - progress_blocks) + "]"

    return (
        f"👤 <b>Имя пользователя:</b> {data.get('username', 'не указано')}\n"
        f"🔄 <b>Статус:</b> {data.get('userStatus', 'неизвестен')}\n"
        f"📅 <b>Осталось дней:</b> {data.get('daysLeft', 0)}\n\n"
        f"📊 <b>Использовано трафика:</b>\n"
        f"{progress_bar} {traffic_percent:.1f}%\n"
        f"▸ {traffic_used:.2f} GiB из {traffic_limit:.2f} GiB"
    )


async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if not update.effective_user:
        logger.error("No effective user in update")
        return

    telegram_user = update.effective_user
    user_config = None

    try:
        user_config = await get_user(telegram_user.id)
    except Exception as e:
        logger.error(f"Error getting user: {e}")

    return_message = f"👤 Профиль: {telegram_user.full_name}\n\n"
    buttons = []

    open_config_button = InlineKeyboardButton(
        "Управлять подпиской",
        web_app=WebAppInfo(url=f"{MINI_APP_URL}/{telegram_user.id}"),
    )
    add_subscription_button = InlineKeyboardButton(
        " + Добавить подписку", callback_data="replace_msg"
    )

    if user_config:
        buttons.append([open_config_button])
        return_message += format_user_data(user_config)

    buttons.append([add_subscription_button])

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=return_message, reply_markup=keyboard, parse_mode="HTML"
            )
            await update.callback_query.answer()
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            await _handle_edit_failure(update, context)
    elif update.message:
        await update.message.reply_text(
            return_message, reply_markup=keyboard, parse_mode="HTML"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    if not update.callback_query or not update.callback_query.message:
        return

    query = update.callback_query
    await query.answer()

    # Store original message ID for fallback
    context.user_data["last_message_id"] = query.message.message_id

    try:
        await query.edit_message_text(
            text="💳 Выберите тарифный план для создания нового ключа:",
            reply_markup=build_keyboard("updated"),
        )
    except telegram.error.BadRequest as e:
        logger.error(f"BadRequest in button_callback: {e}")
        await _handle_edit_failure(update, context)


def build_keyboard(state: Optional[str] = None) -> InlineKeyboardMarkup:
    """Build dynamic keyboard."""
    tariffs = [
        "1 месяц – 178 руб",
        "3 месяца - 450 руб",
        "6 месяцев - 690 руб",
        "12 месяцев - 840 руб",
    ]
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(tariff, callback_data=f"pay:{tariff}")])

    lk_button = InlineKeyboardButton(
        "Личный кабинет",
        callback_data="lk",
    )
    buttons.append([lk_button])
    return InlineKeyboardMarkup(buttons)


async def handle_new_buttons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle new button callbacks."""
    if not update.callback_query:
        return

    query = update.callback_query
    await query.answer(f"You pressed: {query.data}")

    if query.data == "lk":
        await start(update, context)
    elif query.data and query.data.startswith("pay:"):
        await pay_tariff(update, context)


async def pay_tariff(update: Update, context: CallbackContext) -> None:
    """Handle payment for selected tariff."""
    if not update.callback_query or not update.effective_user:
        return

    query = update.callback_query
    await query.answer()

    try:
        if not query.data:
            return

        selected_tariff = query.data.replace("pay:", "")
        context.user_data["selected_tariff"] = selected_tariff

        price = {
            "1 месяц – 178 руб": 17800,
            "3 месяца - 450 руб": 45000,
            "6 месяцев - 690 руб": 69000,
            "12 месяцев - 840 руб": 84000,
        }.get(selected_tariff, 17800)

        title = f"Оплата тарифа: {selected_tariff}"
        description = "Доступ к премиум функциям бота"
        payload = f"tariff_payment_{update.effective_user.id}"
        provider_token = os.getenv("PAYMENT_PROVIDER_TOKEN", "")

        if not provider_token:
            raise ValueError("Payment provider token not configured")

        await context.bot.send_invoice(
            chat_id=(
                query.message.chat_id if query.message else update.effective_user.id
            ),
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency="RUB",
            prices=[LabeledPrice(selected_tariff, price)],
            start_parameter="tariff_payment",
            need_email=True,
            need_phone_number=False,
        )

    except Exception as e:
        logger.error(f"Error in pay_tariff: {e}", exc_info=True)
        if query.message:
            await query.edit_message_text(
                text="⚠️ Произошла ошибка при создании платежа",
                reply_markup=build_keyboard(context.user_data.get("state")),
            )


async def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    await query.answer(ok=True)  # Always confirm for testing


async def successful_payment(update: Update, context: CallbackContext) -> None:
    """Обработка успешного платежа с активацией подписки"""
    payment = update.message.successful_payment
    user = update.effective_user

    try:
        selected_tariff = context.user_data.get("selected_tariff")
        # Сохраняем информацию об оплате в БД
        payment_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "amount": payment.total_amount / 100,
            "tariff": selected_tariff,
            "payment_date": datetime.now(),
            "payload": payment.invoice_payload
        }

        save_payment_to_db(payment_data)
        original_message_id = context.user_data.get("last_message_id")
        if original_message_id:
            await context.bot.edit_message_text(
                chat_id=user.id,
                message_id=original_message_id,
                text=f"🎉 Оплата прошла успешно!\n\n"
                     f"Тариф: {selected_tariff}\n"
                     f"Спасибо за покупку!",
                reply_markup=build_keyboard("premium_active")
            )
        else:
            await update.message.reply_text(
                text=f"🎉 Оплата прошла успешно!\n\n"
                     f"Тариф: {selected_tariff}\n"
                     f"Подписка активна до: {end_date_str}\n\n"
                     f"Спасибо за покупку!",
                reply_markup=build_keyboard("premium_active")
            )

        await context.bot.send_message(
            chat_id=user.id,
            text="Доступна новая подписка!"
        )

    except Exception as e:
        logger.error(f"Error processing payment: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=user.id,
            text="⚠️ Произошла ошибка при активации подписки. Пожалуйста, свяжитесь с поддержкой."
        )

        # Уведомление администратора
        notify_admin(f"Ошибка активации подписки для пользователя {user.id}: {str(e)}")


async def successful_payment(update: Update, context: CallbackContext) -> None:
    """Обработка успешного платежа"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id

    # Сохраняем информацию об оплате в БД
    save_payment_to_db(
        user_id=user_id,
        amount=payment.total_amount/100,
        currency=payment.currency,
        payload=payment.invoice_payload
    )

    # Активируем подписку для пользователя
    activate_subscription(user_id) # также нужно передать данные платежа

    await update.message.reply_text(
        "🎉 Оплата прошла успешно! Подписка активирована.\n\n"
        "Спасибо за покупку!",
        reply_markup=build_keyboard(context.user_data.get('state', None))
    )


async def show_subscription(update: Update, context: CallbackContext) -> None:
    """Handler for checking VPN status."""
    if not update.message or not update.message.from_user:
        return

    try:
        timeout_obj = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(
                f"{VPN_API_URL}/status",
                params={"user_id": update.message.from_user.id},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Open Management Panel",
                                    web_app=WebAppInfo(
                                        url=f"https://your-mini-app.com?user={update.message.from_user.id}"
                                    ),
                                )
                            ]
                        ]
                    )
                    await update.message.reply_text(
                        f"📊 Your VPN Status:\n\n"
                        f"👤 User: {data.get('username', 'N/A')}\n"
                        f"🔒 Status: {data.get('status', 'unknown')}\n"
                        f"📅 Expires: {data.get('expires_at', 'N/A')}\n"
                        f"📊 Traffic: {data.get('traffic_used', 0)}/{data.get('traffic_limit', 0)} GB",
                        reply_markup=keyboard,
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Failed to fetch your VPN status. Please try later."
                    )
    except Exception as e:
        logger.error(f"Status check error: {e}")
        if update.message:
            await update.message.reply_text("🔴 Service temporarily unavailable")
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                f"🚨 Status check failed for user {update.message.from_user.id}: {e}",
            )


async def get_vpn_config(update: Update, context: CallbackContext) -> None:
    """Handler for downloading VPN config."""
    if not update.message or not update.message.from_user:
        return

    try:
        timeout_obj = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(
                f"{VPN_API_URL}/config",
                params={
                    "user_id": update.message.from_user.id,
                    "token": "SECURE_API_TOKEN",
                },
            ) as resp:
                if resp.status == 200:
                    config = await resp.read()
                    await update.message.reply_document(
                        document=config,
                        filename="yourvpn_config.ovpn",
                        caption="🔐 Your VPN configuration file",
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Failed to generate config. Please try later."
                    )
    except Exception as e:
        logger.error(f"Config generation error: {e}")
        if update.message:
            await update.message.reply_text("🔴 Configuration service unavailable")
        if ADMIN_CHAT_ID:
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                f"🚨 Config failed for user {update.message.from_user.id}: {e}",
            )


async def contact_support(update: Update, context: CallbackContext) -> None:
    """Handler for support requests."""
    if not update.message:
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Open Support Chat", url="https://t.me/yourvpn_support"
                )
            ]
        ]
    )
    await update.message.reply_text(
        "🛠 Need help? Contact our support team:\n\n"
        "📧 Email: support@yourvpn.com\n"
        "🌐 Website: https://yourvpn.com/support\n\n"
        "For urgent issues, reply to this message:",
        reply_markup=keyboard,
    )


async def admin_panel(update: Update, context: CallbackContext) -> None:
    """Admin control panel."""
    if not update.message:
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Open Admin Dashboard",
                    web_app=WebAppInfo(url="https://your-mini-app.com/admin"),
                )
            ]
        ]
    )
    await update.message.reply_text(
        "🛠 Admin Panel:\n\n"
        "/users - List all users\n"
        "/stats - Service statistics\n"
        "/broadcast - Send announcement",
        reply_markup=keyboard,
    )


async def error_handler(update: object, context: CallbackContext) -> None:
    """Log errors and send them to admin chat."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    user_info = ""
    if isinstance(update, Update) and update.effective_user:
        user_info = f" for user {update.effective_user.id}"

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            f"🚨 Error occurred{user_info}: {context.error}",
        )


handlers = [
    CommandHandler("start", start),
    CommandHandler("status", show_subscription),
    CommandHandler("config", get_vpn_config),
    CommandHandler("support", contact_support),
    CommandHandler("admin", admin_panel),
    MessageHandler(
        filters.TEXT & filters.Regex(r"^Моя подписка$"),
        show_subscription,
    ),
    CallbackQueryHandler(button_callback, pattern="^replace_msg$"),
    CallbackQueryHandler(handle_new_buttons),
    MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment),
    PreCheckoutQueryHandler(precheckout_callback),
]



def register_handlers(application, handlers):
    """Register handlers"""
    for handler in handlers:
        application.add_handler(handler)

    application.add_error_handler(error_handler)

def main() -> None:
    """Start the bot."""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable not set")

    application = Application.builder().token(bot_token).build()
    register_handlers(application, handlers)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

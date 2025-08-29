# vpnbot/utils.py
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
from django.utils import timezone

import os
import sys
import django
from django.conf import settings

# Добавляем корневую директорию проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django только если он еще не настроен
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()

from main.models import VPNUser, Subscription, Payment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tariff mapping with fallback
TARIFFS = {
    "1month": {
        "name": "1 месяц – 178 руб",
        "duration": 30,
        "price": 17800,
        "traffic_limit": 100  # GB
    },
    "3months": {
        "name": "3 месяца - 450 руб",
        "duration": 90,
        "price": 45000,
        "traffic_limit": 300
    },
    "6months": {
        "name": "6 месяцев - 690 руб",
        "duration": 180,
        "price": 69000,
        "traffic_limit": 600
    },
    "12months": {
        "name": "12 месяцев - 840 руб",
        "duration": 365,
        "price": 84000,
        "traffic_limit": 1200
    }
}

def get_tariff_by_id(tariff_id: str) -> Dict[str, Any]:
    """Safely returns tariff details by ID with fallback to default 1month tariff"""
    try:
        tariff_id = tariff_id.lower()
        if tariff_id not in TARIFFS:
            logger.warning(f"Unknown tariff ID: {tariff_id}. Using default.")
            tariff_id = "1month"
        return TARIFFS[tariff_id]
    except Exception as e:
        logger.error(f"Error getting tariff: {e}", exc_info=True)
        return TARIFFS["1month"]

def get_or_create_user(user_id: int, username: str = None,
                      first_name: str = None, last_name: str = None) -> VPNUser:
    """Get or create VPNUser with telegram user data"""
    try:
        user, created = VPNUser.objects.get_or_create(
            user_id=str(user_id),
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }
        )
        if created:
            logger.info(f"Created new VPNUser: {user}")
        return user
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}", exc_info=True)
        raise

def save_payment_to_db(user_id: int, amount: float, currency: str,
                      tariff_id: str, payload: str = None) -> Payment:
    """Save payment information to database"""
    try:
        tariff = get_tariff_by_id(tariff_id)
        user = get_or_create_user(user_id)

        # Create new subscription
        subscription = Subscription.objects.create(
            user=user,
            vpn_username=f"vpnuser_{user_id}_{datetime.now().strftime('%Y%m%d')}",
            status=Subscription.STATUS_PENDING,
            tariff=tariff_id,
            expires_at=timezone.now() + timedelta(days=tariff['duration']),
            traffic_limit=tariff['traffic_limit']
        )

        # Create payment record
        payment = Payment.objects.create(
            subscription=subscription,
            amount=amount,
            currency=currency,
            payload=payload
        )

        logger.info(f"Payment saved: {payment.id} for user {user_id}")
        return payment

    except Exception as e:
        logger.error(f"Error saving payment: {e}", exc_info=True)
        raise

def activate_subscription(payment_id: int) -> Optional[Subscription]:
    """Activate subscription after successful payment"""
    try:
        payment = Payment.objects.get(id=payment_id)
        subscription = payment.subscription

        # Update subscription status
        subscription.status = Subscription.STATUS_ACTIVE
        subscription.save()

        # Generate VPN config (placeholder - implement your actual VPN setup)
        subscription.vpn_config = generate_vpn_config(subscription)
        subscription.save()

        logger.info(f"Subscription activated: {subscription.id}")
        return subscription

    except Payment.DoesNotExist:
        logger.error(f"Payment not found: {payment_id}")
    except Exception as e:
        logger.error(f"Error activating subscription: {e}", exc_info=True)
    return None

def generate_vpn_config(subscription: Subscription) -> str:
    """Generate VPN configuration for user (placeholder implementation)"""
    # Replace with your actual VPN config generation logic
    return f"""<VPN config for {subscription.vpn_username}>
# Expires: {subscription.expires_at.date()}
# Traffic limit: {subscription.traffic_limit}GB"""

def notify_admin(message: str, chat_id: str = None) -> bool:
    """Send notification to admin"""
    try:
        if not message:
            raise ValueError("Empty message")

        # Implement your actual notification logic
        # Example: send_telegram_message(chat_id or ADMIN_CHAT_ID, message)
        logger.info(f"Admin notification: {message[:100]}...")
        return True

    except Exception as e:
        logger.error(f"Error notifying admin: {e}", exc_info=True)
        return False

def check_subscription_status(user_id: int) -> Dict[str, Any]:
    """Check user's active subscription status"""
    try:
        user = VPNUser.objects.get(user_id=str(user_id))
        active_subs = user.subscriptions.filter(
            status=Subscription.STATUS_ACTIVE,
            expires_at__gt=timezone.now()
        ).order_by('-expires_at').first()

        if not active_subs:
            return {'has_active': False}

        return {
            'has_active': True,
            'expires_at': active_subs.expires_at,
            'days_left': (active_subs.expires_at - timezone.now()).days,
            'traffic_used': active_subs.traffic_used,
            'traffic_limit': active_subs.traffic_limit,
            'tariff': active_subs.get_tariff_display()
        }

    except VPNUser.DoesNotExist:
        return {'has_active': False}
    except Exception as e:
        logger.error(f"Error checking subscription: {e}", exc_info=True)
        return {'error': str(e)}

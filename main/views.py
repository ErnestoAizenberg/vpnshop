import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Subscription

logger = logging.getLogger("main")

def home_view(request, vpn_username):  # Теперь принимаем vpn_username вместо subscription_id
    subscription = get_object_or_404(Subscription, vpn_username=vpn_username)

    if request.client_type == "vpn":
        logger.info(f"VPN config request for {vpn_username}")
        # Здесь должен быть код генерации/отдачи конфига VPN
        return JsonResponse({
            "config": subscription.vpn_config,
            "expires_at": subscription.expires_at.isoformat()
        })

    context = {
        "user": subscription.user,  # Для совместимости с шаблоном
        "subscription": subscription
    }
    return render(request, "main/home.html", context=context)


def get_subscription(request, vpn_username):  # Используем vpn_username как ключ
    try:
        subscription = Subscription.objects.get(vpn_username=vpn_username)

        return JsonResponse({
            "userId": str(subscription.user.user_id),
            "username": vpn_username,  # Теперь точно соответствует запрошенному
            "userStatus": subscription.status,
            "expiresAt": subscription.expires_at.strftime("%d.%m.%Y"),
            "daysLeft": subscription.days_left,
            "trafficUsed": subscription.traffic_used,
            "trafficLimit": subscription.traffic_limit,
            "trafficPercent": round(
                (subscription.traffic_used / subscription.traffic_limit) * 100, 1
            ) if subscription.traffic_limit > 0 else 0,
            "configUrl": f"/download-config/{vpn_username}/"  # Пример URL для скачивания конфига
        })

    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for username: {vpn_username}")
        return JsonResponse({"error": "VPN user not found"}, status=404)
    except Exception as e:
        logger.error(f"Error in get_subscription: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)

import logging

from django.http import JsonResponse
from django.shortcuts import render

from .models import VPNUser

logger = logging.getLogger("main")


def home_view(request, user_id):
    try:
        user = VPNUser.objects.get(user_id=user_id)
    except VPNUser.DoesNotExist:
        return JsonResponse({"status": 404})

    if request.client_type == "vpn":
        logger.info("request type is vpn, returning vpn config")
        return JsonResponse({})

    context = {"user": user}
    return render(request, "main/home.html", context=context)


def get_subscription(request, user_id):
    try:
        user = VPNUser.objects.get(user_id=user_id)
        return JsonResponse(
            {
                "userId": str(user.user_id),
                "username": user.vpn_username,
                "userStatus": user.status,
                "expiresAt": user.expires_at.strftime("%d.%m.%Y"),
                "daysLeft": user.days_left,
                "trafficUsed": user.traffic_used,
                "trafficLimit": user.traffic_limit,
                "trafficPercent": round(
                    (user.traffic_used / user.traffic_limit) * 100, 1
                ),
            }
        )
    except Exception as e:
        logger.error(f"Error in get_user view: {str(e)}", exc_info=True)
    return JsonResponse(
        {"error": "Unexpected error occured, please contaxt suppott", "status": 500}
    )

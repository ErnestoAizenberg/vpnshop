# models.py
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.html import format_html


class VPNUser(models.Model):
    """Main user model that stores Telegram user information"""
    user_id = models.CharField(
        unique=True, verbose_name="Telegram ID", max_length=50
    )
    username = models.CharField(
        max_length=100, verbose_name="Telegram username", blank=True, null=True
    )
    first_name = models.CharField(
        max_length=100, verbose_name="First name", blank=True, null=True
    )
    last_name = models.CharField(
        max_length=100, verbose_name="Last name", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VPN User"
        verbose_name_plural = "VPN Users"

    def __str__(self):
        return f"{self.user_id} ({self.username or self.first_name})"


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_PENDING = "pending"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_PENDING, "Pending"),
    ]

    TARIFF_1MONTH = "1month"
    TARIFF_3MONTHS = "3months"
    TARIFF_6MONTHS = "6months"
    TARIFF_12MONTHS = "12months"
    TARIFF_CHOICES = [
        (TARIFF_1MONTH, "1 Month - 178 RUB"),
        (TARIFF_3MONTHS, "3 Months - 450 RUB"),
        (TARIFF_6MONTHS, "6 Months - 690 RUB"),
        (TARIFF_12MONTHS, "12 Months - 840 RUB"),
    ]

    user = models.ForeignKey(
        VPNUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    vpn_username = models.CharField(max_length=100, verbose_name="VPN Username")
    vpn_config = models.TextField(verbose_name="VPN Configuration")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    tariff = models.CharField(max_length=20, choices=TARIFF_CHOICES)
    expires_at = models.DateTimeField(verbose_name="Expiration Date")
    traffic_used = models.FloatField(
        verbose_name="Traffic Used (GB)", default=0
    )
    traffic_limit = models.FloatField(
        verbose_name="Traffic Limit (GB)", default=100
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-expires_at"]

    @property
    def days_left(self):
        if not self.expires_at:
            return 0
        delta = self.expires_at - timezone.now()
        return delta.days if delta.days > 0 else 0

    @property
    def traffic_percentage(self):
        if self.traffic_limit == 0:
            return 0
        return round((self.traffic_used / self.traffic_limit) * 100, 2)

    def __str__(self):
        return f"{self.vpn_username} ({self.user.user_id})"


class Payment(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    provider_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payload = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment #{self.id} for {self.subscription}"


@admin.register(VPNUser)
class VPNUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "username", "first_name", "subscriptions_count")
    search_fields = ("user_id", "username", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at")

    def subscriptions_count(self, obj):
        return obj.subscriptions.count()
    subscriptions_count.short_description = "Subscriptions"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "vpn_username",
        "user_info",
        "status_colored",
        "tariff",
        "expires_at",
        "days_left_display",
        "traffic_usage",
        "created_at",
    )
    list_filter = ("status", "tariff", "created_at")
    search_fields = ("vpn_username", "user__user_id", "user__username")
    readonly_fields = (
        "days_left",
        "traffic_percentage",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "expires_at"

    fieldsets = (
        (None, {"fields": ("user", "vpn_username", "vpn_config", "status", "tariff")}),
        (
            "Traffic",
            {"fields": ("traffic_used", "traffic_limit", "traffic_percentage")},
        ),
        ("Dates", {"fields": ("expires_at", "created_at", "updated_at")}),
    )

    @admin.display(description="User")
    def user_info(self, obj):
        return f"{obj.user.user_id} ({obj.user.username or obj.user.first_name})"

    @admin.display(description="Status")
    def status_colored(self, obj):
        colors = {
            Subscription.STATUS_ACTIVE: "green",
            Subscription.STATUS_EXPIRED: "red",
            Subscription.STATUS_PENDING: "orange",
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    @admin.display(description="Days Left")
    def days_left_display(self, obj):
        days = obj.days_left
        if days <= 3:
            color = "red"
        elif days <= 7:
            color = "orange"
        else:
            color = "green"
        return format_html('<span style="color: {};">{}</span>', color, days)

    @admin.display(description="Traffic Usage")
    def traffic_usage(self, obj):
        percentage = obj.traffic_percentage
        if percentage > 90:
            color = "red"
        elif percentage > 70:
            color = "orange"
        else:
            color = "green"
        return format_html(
            '{} GB / {} GB (<span style="color: {};">{}%</span>)',
            obj.traffic_used,
            obj.traffic_limit,
            color,
            percentage,
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "subscription", "amount", "currency", "created_at")
    list_filter = ("currency", "created_at")
    search_fields = (
        "subscription__vpn_username",
        "subscription__user__user_id",
        "provider_payment_id",
    )
    readonly_fields = ("created_at",)

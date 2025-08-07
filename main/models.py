from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.html import format_html


class VPNUser(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Активна"),
        (STATUS_EXPIRED, "Истекла"),
    ]

    user_id = models.CharField(
        unique=True, verbose_name="Telegram ID", max_length=50
    )  # Telegram user_id
    vpn_username = models.CharField(max_length=100, verbose_name="VPN Имя пользователя")
    vpn_config = models.CharField(
        max_length=100, verbose_name="Ключ к конфигу VPN"
    )  # Може юыть это просто ссылка на конфиг, может ID, если ID то нужно решать с ID для провайдеров

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name="Статус",
    )
    expires_at = models.DateTimeField(verbose_name="Дата истечения")
    traffic_used = models.FloatField(
        verbose_name="Использовано трафика (ГБ)"
    )  # В гигабайтах
    traffic_limit = models.FloatField(verbose_name="Лимит трафика (ГБ)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "VPN Пользователь"
        verbose_name_plural = "VPN Пользователи"
        ordering = ["-expires_at"]

    @property
    def days_left(self):
        if not self.expires_at:
            return 0

        delta = self.expires_at - timezone.now()
        return delta.days if delta.days > 0 else 0

    @property
    def traffic_percentage(self):
        if self.traffic_limit == 0 or not self.traffic_limit or not self.traffic_used:
            return 0
        return round((self.traffic_used / self.traffic_limit) * 100, 2)

    def __str__(self):
        return f"{self.vpn_username} ({self.user_id})"


@admin.register(VPNUser)
class VPNUserAdmin(admin.ModelAdmin):
    list_display = (
        "vpn_username",
        "user_id",
        "status_colored",
        "expires_at",
        "days_left_display",
        "traffic_used",
        "traffic_limit",
        "traffic_percentage_display",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("vpn_username", "user_id")
    readonly_fields = ("days_left", "traffic_percentage", "created_at", "updated_at")
    date_hierarchy = "expires_at"
    list_per_page = 20

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user_id", "vpn_username", "status", "vpn_config")},
        ),
        (
            "Статистика использования",
            {"fields": ("traffic_used", "traffic_limit", "traffic_percentage")},
        ),
        ("Срок действия", {"fields": ("expires_at", "days_left")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Осталось дней", ordering="expires_at")
    def days_left_display(self, obj):
        days = obj.days_left
        if days <= 3:
            color = "red"
        elif days <= 7:
            color = "orange"
        else:
            color = "green"
        return format_html('<span style="color: {};">{}</span>', color, days)

    @admin.display(description="Статус")
    def status_colored(self, obj):
        color = "green" if obj.status == VPNUser.STATUS_ACTIVE else "red"
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_status_display()
        )

    @admin.display(description="Использовано трафика %")
    def traffic_percentage_display(self, obj):
        percentage = obj.traffic_percentage
        if percentage > 90:
            color = "red"
        elif percentage > 70:
            color = "orange"
        else:
            color = "green"
        return format_html('<span style="color: {};">{}%</span>', color, percentage)

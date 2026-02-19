from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Shop, Client


@admin.register(Shop)
class ShopAdmin(ModelAdmin):
    list_display = (
        "name_display",
        "clients_count_badge",
    )
    search_fields = ("name",)
    ordering = ("name",)

    # TUZATILDI: header=True bo'lganda tuple qaytarish shart
    @display(description="Do‘kon nomi", header=True)
    def name_display(self, obj):
        # Format: (Sarlavha, Ikonka_yoki_Izoh)
        return obj.name, "storefront"

    @display(description="Mijozlar soni", label=True)
    def clients_count_badge(self, obj):
        count = obj.clients.count()
        label_color = "success" if count > 0 else "warning"
        return f"{count} ta mijoz", label_color

    def get_list_display_metrics(self, request):
        return [
            {
                "title": "Jami do‘konlar",
                "value": Shop.objects.count(),
                "icon": "store",
                "color": "primary",
            },
        ]


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = (
        "full_name_display",
        "phone_link",
        "shop_badge",
        "filial_name",
        "location_link",
    )

    list_filter = ("shop", "filial_name")
    search_fields = ("full_name", "phone", "filial_name")
    list_per_page = 25
    ordering = ("-id",)

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            "fields": ("telegram_id", "full_name", "phone"),
            "classes": ["tab"],
        }),
        (_("Do‘kon ma'lumotlari"), {
            "fields": ("shop", "filial_name"),
            "classes": ["tab"],
        }),
        (_("Joylashuv (GPS)"), {
            "fields": ("latitude", "longitude"),
            "classes": ["tab"],
        }),
    )

    # TUZATILDI: header=True uchun tuple qaytarildi
    @display(description="Mijoz", header=True)
    def full_name_display(self, obj):
        return obj.full_name, "person"

    @display(description="Telefon")
    def phone_link(self, obj):
        if not obj.phone:
            return "-"
        return format_html(
            '<div class="flex items-center gap-2">'
            '<span class="material-symbols-outlined text-blue-500 text-sm">call</span>'
            '<a href="tel:{}" class="text-blue-600 font-medium hover:underline">{}</a>'
            '</div>', obj.phone, obj.phone
        )

    @display(description="Do‘kon", label=True)
    def shop_badge(self, obj):
        val = obj.shop.name if obj.shop else "-"
        return val, "success"

    @display(description="Joylashuv")
    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            # Google Maps URL formati yaxshilandi
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html(
                '<div class="flex items-center gap-1">'
                '<span class="material-symbols-outlined text-indigo-500 text-sm">location_on</span>'
                '<a href="{}" target="_blank" class="text-indigo-500 font-medium hover:underline">'
                'Xaritada ko‘rish</a>'
                '</div>', url
            )
        return format_html('<span class="text-gray-400 italic">Joylashuv yo‘q</span>')

    def get_list_display_metrics(self, request):
        return [
            {
                "title": "Jami mijozlar",
                "value": Client.objects.count(),
                "icon": "group",
                "color": "info",
            },
            {
                "title": "Tizimdagi faollik",
                "value": Client.objects.all().count(),
                "icon": "analytics",
                "color": "success",
            },
        ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shop')

from django.contrib import admin
from .models import Shop, Client


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "clients_count",
    )

    search_fields = ("name",)
    ordering = ("name",)

    def clients_count(self, obj):
        return obj.clients.count()
    clients_count.short_description = "Mijozlar soni"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "shop",
        "filial_name",
        "location_short",
    )

    list_filter = (
        "shop",
        "filial_name",
    )

    search_fields = (
        "full_name",
        "phone",
        "filial_name",
    )

    # readonly_fields = (
    #     "latitude",
    #     "longitude",
    # )

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("telegram_id", "full_name", "phone")
        }),
        ("Do‘kon ma'lumotlari", {
            "fields": ("shop", "filial_name")
        }),
        ("Joylashuv (GPS)", {
            "fields": ("latitude", "longitude")
        }),
    )

    ordering = ("-id",)

    list_per_page = 25

    def location_short(self, obj):
        return f"{obj.latitude}, {obj.longitude}"

    location_short.short_description = "Joylashuv"

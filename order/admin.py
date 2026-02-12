from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Order, OrderItem


# =========================
# YORDAMCHI FUNKSIYA
# =========================

def format_currency(amount):
    """Raqamni 1 000 000 ko'rinishida formatlash uchun umumiy funksiya"""
    if amount is not None:
        try:
            # Mingliklarni probel bilan ajratish va nuqtadan keyingi nollarni olib tashlash
            formatted = "{:,.0f}".format(float(amount)).replace(",", " ")
            return format_html("{}", formatted)
        except (ValueError, TypeError):
            return "-"
    return "-"


# =========================
# INLINE: ORDER ITEM
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)

    fields = (
        "product",
        "quantity",
        "formatted_price",
        "formatted_summary",
    )

    readonly_fields = ("formatted_price", "formatted_summary")

    def formatted_price(self, obj):
        return format_currency(obj.price)

    formatted_price.short_description = "Narxi (dona)"

    def formatted_summary(self, obj):
        return format_currency(obj.summary)

    formatted_summary.short_description = "Jami"


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id_display",
        "shop",
        "get_filial",
        "status",
        "formatted_total",
        "created_at",
    )

    list_filter = (
        "status",
        "shop",
        "client__filial_name",
        "created_at",
    )

    search_fields = (
        "id",
        "client__full_name",
        "client__phone",
        "client__filial_name",
        "shop__name",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)

    readonly_fields = (
        "total_price",
        "created_at",
        "confirmed_at",
        "delivered_at",
    )

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": (
                "shop",
                "client",
                "status",
                "comment",
            )
        }),
        ("Moliyaviy ma'lumotlar", {
            "fields": (
                "total_price",
            )
        }),
        ("Vaqtlar", {
            "fields": (
                "created_at",
                "confirmed_at",
                "delivered_at",
            )
        }),
    )

    actions = (
        "mark_confirmed",
        "mark_delivered",
    )

    # =====================
    # DISPLAY METHODS
    # =====================

    def id_display(self, obj):
        return f"#{obj.id}"

    id_display.short_description = "ID"

    def get_filial(self, obj):
        return obj.client.filial_name if obj.client else "-"

    get_filial.short_description = "Filial"
    get_filial.admin_order_field = "client__filial_name"

    def formatted_total(self, obj):
        return format_currency(obj.total_price)

    formatted_total.short_description = "Umumiy summa"
    formatted_total.admin_order_field = "total_price"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'shop')

    # =====================
    # ACTIONS
    # =====================

    @admin.action(description="Tasdiqlangan deb belgilash")
    def mark_confirmed(self, request, queryset):
        queryset.filter(status=Order.Status.CREATED).update(
            status=Order.Status.CONFIRMED,
            confirmed_at=timezone.now()
        )

    @admin.action(description="Yetkazilgan deb belgilash")
    def mark_delivered(self, request, queryset):
        queryset.filter(status=Order.Status.CONFIRMED).update(
            status=Order.Status.DELIVERED,
            delivered_at=timezone.now()
        )


# =========================
# ORDER ITEM ADMIN
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "formatted_price",
        "formatted_summary",
    )

    list_filter = ("product__category", "order")
    search_fields = ("product__name", "order__client__full_name")
    autocomplete_fields = ("product",)

    def formatted_price(self, obj):
        return format_currency(obj.price)

    formatted_price.short_description = "Narxi"

    def formatted_summary(self, obj):
        return format_currency(obj.summary)

    formatted_summary.short_description = "Jami summa"

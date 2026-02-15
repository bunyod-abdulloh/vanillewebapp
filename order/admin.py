from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Order, OrderItem


# =========================
# 1. YORDAMCHI FUNKSIYALAR
# =========================
def format_currency(amount):
    """Raqamni chiroyli formatda chiqarish"""
    if amount is not None:
        try:
            formatted = "{:,.0f}".format(float(amount)).replace(",", " ")
            return format_html("{}", formatted)
        except (ValueError, TypeError):
            return "-"
    return "-"


# =========================
# 2. INLINES
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "formatted_price", "formatted_summary")
    readonly_fields = ("formatted_price", "formatted_summary")

    def formatted_price(self, obj):
        return format_currency(obj.price)

    formatted_price.short_description = "Narxi (dona)"

    def formatted_summary(self, obj):
        return format_currency(obj.summary)

    formatted_summary.short_description = "Jami"


# =========================
# 3. ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # List ko'rinishi sozlamalari
    list_display = ("id_display", "shop", "get_filial", "status", "formatted_total", "created_at")
    list_filter = ("status", "shop", "client__filial_name", "created_at")
    search_fields = ("id", "client__full_name", "client__phone", "client__filial_name", "shop__name")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)

    # Standart readonly maydonlar
    readonly_fields = ("total_price", "created_at", "confirmed_at", "delivered_at")
    actions = ("mark_confirmed", "mark_delivered", "mark_canceled")
    fieldsets = (
        ("Asosiy ma'lumotlar", {"fields": ("shop", "client", "status", "comment")}),
        ("Moliyaviy ma'lumotlar", {"fields": ("total_price",)}),
        ("Vaqtlar", {"fields": ("created_at", "confirmed_at", "delivered_at")}),
    )

    # --- DINAMIK RUXSATLAR (Yordamchi admin uchun) ---

    def get_readonly_fields(self, request, obj=None):
        """Yordamchi adminga statusdan boshqa hamma narsani readonly qilish"""
        if not request.user.is_superuser:
            # Fieldset-dagi barcha maydonlarni yig'ib olamiz
            all_fields = []
            for group, options in self.fieldsets:
                all_fields.extend(options.get('fields', []))
            # 'status' dan boshqa hammasini readonly qaytaramiz
            return [f for f in all_fields if f != 'status']
        return self.readonly_fields

    def get_inline_instances(self, request, obj=None):
        """Yordamchi adminga OrderItem-larni ko'rsatmaslik"""
        if not request.user.is_superuser:
            return []
        return super().get_inline_instances(request, obj)

    def has_add_permission(self, request):
        """Faqat superadmin yangi order qo'sha oladi"""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Faqat superadmin o'chira oladi"""
        return request.user.is_superuser

    # --- DISPLAY METODLARI ---
    def id_display(self, obj):
        return f"#{obj.id}"

    id_display.short_description = "ID"

    def get_filial(self, obj):
        return obj.client.filial_name if obj.client else "-"

    get_filial.short_description = "Filial"

    def formatted_total(self, obj):
        return format_currency(obj.total_price)

    formatted_total.short_description = "Umumiy summa"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'shop')

    # --- ACTIONS ---
    @admin.action(description="Tanlanganlarni 'Tasdiqlandi' holatiga o'tkazish")
    def mark_confirmed(self, request, queryset):
        # Hech qanday filtrsiz barcha tanlanganlarni yangilaymiz
        count = queryset.update(
            status="confirmed",
            confirmed_at=timezone.now()
        )
        self.message_user(request, f"{count} ta buyurtma 'Tasdiqlandi' holatiga o'tkazildi.")

    @admin.action(description="Tanlanganlarni 'Yetkazildi' holatiga o'tkazish")
    def mark_delivered(self, request, queryset):
        # Hech qanday filtrsiz barcha tanlanganlarni yangilaymiz
        count = queryset.update(
            status="delivered",
            delivered_at=timezone.now()
        )
        self.message_user(request, f"{count} ta buyurtma 'Yetkazildi' holatiga o'tkazildi.")

    @admin.action(description="Tanlanganlarni 'Bekor qilindi' holatiga o'tkazish")
    def mark_canceled(self, request, queryset):
        # Hech qanday filtrsiz barcha tanlanganlarni yangilaymiz
        count = queryset.update(
            status="canceled",
            delivered_at=timezone.now()
        )
        self.message_user(request, f"{count} ta buyurtma 'Bekor qilindi' holatiga o'tkazildi.")

# =========================
# 4. BOSHQA MODELLARNI YASHIRISH
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        """Bu model yordamchi admin menyusida umuman ko'rinmaydi"""
        return request.user.is_superuser

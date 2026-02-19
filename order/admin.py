from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export import resources, fields
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.decorators import action, display

from .models import Order, OrderItem


# =========================
# 1. YORDAMCHI FUNKSIYALAR
# =========================
def format_currency_text(amount):
    """Raqamni chiroyli formatda chiqarish"""
    if amount is not None:
        try:
            formatted = "{:,.0f}".format(float(amount)).replace(",", " ")
            return format_html('<span class="font-semibold text-gray-900">{} UZS</span>', formatted)
        except (ValueError, TypeError):
            return "-"
    return "-"


# =========================
# 2. INLINES
# =========================
class OrderItemInline(TabularInline):
    model = OrderItem
    tab = True
    extra = 0
    verbose_name_plural = "Buyurtma tarkibi"
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "formatted_price", "formatted_summary")
    readonly_fields = ("formatted_price", "formatted_summary")

    @display(description="Narxi (dona)")
    def formatted_price(self, obj):
        return format_currency_text(obj.price)

    @display(description="Jami")
    def formatted_summary(self, obj):
        return format_currency_text(obj.summary)

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# =========================
# 3. EXCEL RESURSI
# =========================
class OrderItemResource(resources.ModelResource):
    restoran_nomi = fields.Field(column_name='Restoran', attribute='order__shop__name')
    filial = fields.Field(column_name='Filial', attribute='order__client__filial_name')
    mijoz_ismi = fields.Field(column_name='Mijoz', attribute='order__client__full_name')
    mahsulot_kategoriyasi = fields.Field(column_name="Kategoriya", attribute='product__category__name')
    mahsulot_nomi = fields.Field(column_name='Mahsulot', attribute='product__name')
    sana = fields.Field(column_name='Sotib olingan sana', attribute='order__created_at')

    class Meta:
        model = OrderItem
        fields = ('restoran_nomi', 'filial', 'mijoz_ismi', 'mahsulot_kategoriyasi', 'mahsulot_nomi', 'quantity',
                  'price', 'summary', 'sana')


# =========================
# 4. ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm

    list_display = ("id_display", "shop_badge", "get_filial", "status_badge", "formatted_total", "created_at")
    list_filter = ("status", "shop", "client__filial_name", "created_at")
    search_fields = ("id", "client__full_name", "client__phone", "client__filial_name", "shop__name")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)

    readonly_fields = ("formatted_total_field", "created_at", "confirmed_at", "delivered_at")

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            "fields": ("shop", "client", "status", "comment"),
            "classes": ["tab"],
        }),
        (_("Vaqtlar"), {
            "fields": ("created_at", "confirmed_at", "delivered_at"),
            "classes": ["tab"],
        }),
        (_("Moliyaviy ma'lumotlar"), {
            "fields": ("formatted_total_field",),
            "classes": ["tab"],
            "inlines": ["OrderItemInline"],
        }),
    )

    # --- DISPLAY METODLARI ---
    @display(description="ID")
    def id_display(self, obj):
        return format_html('<span class="font-bold text-indigo-600">#{}</span>', obj.id)

    @display(description="Restoran", label=True)
    def shop_badge(self, obj):
        return obj.shop.name if obj.shop else "-"

    @display(description="Filial")
    def get_filial(self, obj):
        return obj.client.filial_name if obj.client else "-"

    @display(description="Status")
    def status_badge(self, obj):
        colors = {
            'confirmed': 'bg-green-100 text-green-700 border-green-200',
            'delivered': 'bg-blue-100 text-blue-700 border-blue-200',
            'canceled': 'bg-red-100 text-red-700 border-red-200',
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-700 border-gray-200')
        return format_html(
            '<span class="px-2 py-0.5 rounded-md border font-medium text-xs {}">{}</span>',
            color_class,
            obj.get_status_display()
        )

    @display(description="Umumiy summa")
    def formatted_total(self, obj):
        return format_currency_text(obj.total_price)

    @display(description="Jami buyurtma summasi")
    def formatted_total_field(self, obj):
        return format_currency_text(obj.total_price)

    # --- DASHBOARD METRICS ---
    def get_list_display_metrics(self, request):
        from django.db.models import Sum, Avg
        stats = Order.objects.aggregate(total_sum=Sum('total_price'), avg_sale=Avg('total_price'))

        return [
            {
                "title": "Jami tushum",
                "value": f"{int(stats['total_sum'] or 0):,} UZS".replace(",", " "),
                "icon": "payments",
                "color": "success",
            },
            {
                "title": "Jami buyurtmalar",
                "value": Order.objects.count(),
                "icon": "shopping_cart",
                "color": "primary",
            },
            {
                "title": "O'rtacha savdo",
                "value": f"{int(stats['avg_sale'] or 0):,} UZS".replace(",", " "),
                "icon": "analytics",
                "color": "info",
            },
        ]

    # --- ACTIONS ---
    @action(description="Tanlanganlarni 'Tasdiqlandi' holatiga o'tkazish")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed", confirmed_at=timezone.now())

    @action(description="Tanlanganlarni 'Yetkazildi' holatiga o'tkazish")
    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered", delivered_at=timezone.now())

    @action(description="Tanlanganlarni 'Bekor qilindi' holatiga o'tkazish")
    def mark_canceled(self, request, queryset):
        queryset.update(status="canceled", delivered_at=timezone.now())

    actions = ["mark_confirmed", "mark_delivered", "mark_canceled"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'shop')

    # Ruxsatlar
    def has_add_permission(self, request): return request.user.is_superuser

    def has_delete_permission(self, request, obj=None): return request.user.is_superuser

    def has_export_permission(self, request): return request.user.is_superuser

    def has_import_permission(self, request): return request.user.is_superuser


# =========================
# 5. ORDER ITEM ADMIN
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    resource_class = OrderItemResource

    list_display = ('order', 'product', 'quantity', 'summary_display')
    list_filter = ('order', 'product', 'quantity', 'price', 'summary')

    @display(description="Jami")
    def summary_display(self, obj):
        return format_currency_text(obj.summary)

    def has_module_permission(self, request): return request.user.is_superuser

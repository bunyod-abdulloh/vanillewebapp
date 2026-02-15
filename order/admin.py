from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

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
    verbose_name = ""
    verbose_name_plural = "Buyurtma tarkibi"
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "formatted_price", "formatted_summary")
    readonly_fields = ("formatted_price", "formatted_summary")

    def formatted_price(self, obj):
        return format_currency(obj.price)
    formatted_price.short_description = "Narxi (dona)"

    def formatted_summary(self, obj):
        return format_currency(obj.summary)
    formatted_summary.short_description = "Jami"

    # --- YANGI: Yordamchi admin uchun faqat o'qish rejimi ---
    def has_add_permission(self, request, obj=None):
        # Faqat superadmin yangi mahsulot qo'sha oladi
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Faqat superadmin mavjud mahsulotni o'zgartira oladi
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Faqat superadmin o'chira oladi
        return request.user.is_superuser


# =========================
# 3. ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    # List ko'rinishi sozlamalari
    list_display = ("id_display", "shop", "get_filial", "status", "formatted_total", "created_at")
    list_filter = ("status", "shop", "client__filial_name", "created_at")
    search_fields = ("id", "client__full_name", "client__phone", "client__filial_name", "shop__name")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)

    # Standart readonly maydonlar
    actions = ("mark_confirmed", "mark_delivered", "mark_canceled")
    readonly_fields = ("formatted_total_field", "created_at", "confirmed_at", "delivered_at")

    fieldsets = (
        ("ASOSIY MA'LUMOTLAR", {"fields": ("shop", "client", "status", "comment")}),
        ("VAQTLAR", {"fields": ("created_at", "confirmed_at", "delivered_at")}),
        ("MOLIYAVIY MA'LUMOTLAR", {"fields": ("formatted_total_field",)}),
    )

    # --- DINAMIK RUXSATLAR (Yordamchi admin uchun) ---

    def get_inline_instances(self, request, obj=None):
        """
        Endi barcha foydalanuvchilar (shu jumladan yordamchi admin ham)
        OrderItemInline-ni ko'ra oladi.
        """
        return super().get_inline_instances(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """Yordamchi adminga statusdan boshqa hamma narsani readonly qilish"""
        if not request.user.is_superuser:
            all_fields = []
            for group, options in self.fieldsets:
                all_fields.extend(options.get('fields', []))
            return [f for f in all_fields if f != 'status']
        return self.readonly_fields

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

    def formatted_total_field(self, obj):
        return format_currency(obj.total_price)

    formatted_total_field.short_description = "Jami buyurtma summasi"

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

    def has_export_permission(self, request):
        """Eksport tugmasi faqat superadminga chiqadi"""
        return request.user.is_superuser

    def has_import_permission(self, request):
        """Import tugmasi faqat superadminga chiqadi"""
        return request.user.is_superuser

# =========================
# 4. EXCEL RESURSI
# =========================
class OrderItemResource(resources.ModelResource):
    restoran_nomi = fields.Field(
        column_name='Restoran',
        attribute='order__shop__name'
    )
    filial = fields.Field(
        column_name='Filial',
        attribute='order__client__filial_name'
    )
    mijoz_ismi = fields.Field(
        column_name='Mijoz',
        attribute='order__client__full_name'
    )
    mahsulot_kategoriyasi = fields.Field(
        column_name="Kategoriya",
        attribute='product__category__name'
    )
    mahsulot_nomi = fields.Field(
        column_name='Mahsulot',
        attribute='product__name'
    )
    sana = fields.Field(
        column_name='Sotib olingan sana',
        attribute='order__created_at'
    )

    class Meta:
        model = OrderItem
        fields = ('restoran_nomi', 'filial', 'mijoz_ismi', 'mahsulot_kategoriyasi', 'mahsulot_nomi', 'quantity',
                  'price', 'summary', 'sana')
        export_order = fields


# =========================
# 5. ORDER ITEM ADMIN (Birlashtirilgan)
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    list_display = ('order', 'product', 'quantity', 'summary')
    list_filter = ('order', 'product', 'quantity', 'price', 'summary')

    def has_module_permission(self, request):
        """Yordamchi admin menyusida ko'rinmaydi, faqat Superadmin ko'radi"""
        return request.user.is_superuser

    def has_export_permission(self, request):
        """Faqat superadmin Excelga yuklay oladi"""
        return request.user.is_superuser

    def has_import_permission(self, request):
        """Import tugmasi faqat superadminga chiqadi"""
        return request.user.is_superuser

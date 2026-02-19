from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = (
        "name_display",
        "products_count",
    )
    search_fields = ("name",)

    @display(description="Kategoriya nomi")
    def name_display(self, obj):
        return obj.name

    @display(description="Mahsulotlar soni", label=True)
    def products_count(self, obj):
        # product_set o'rniga to'g'ridan-to'g'ri Product modelidan filter qilamiz
        count = Product.objects.filter(category=obj).count()
        return f"{count} ta mahsulot"


@admin.register(Product)
class ProductAdmin(ModelAdmin):  # Unfold ModelAdmin
    list_display = (
        "name_display",
        "category_badge",
        "formatted_price",
        "availability_status",
    )

    list_filter = (
        "category",
        "price",
        "is_available",
    )

    search_fields = (
        "name",
        "category__name",
    )

    # Tahrirlash sahifasini zamonaviy Tab ko'rinishiga keltirish
    fieldsets = (
        (_("Mahsulot ma'lumotlari"), {
            "fields": ("name", "category", "description"),
            "classes": ["tab"],
        }),
        (_("Narx va Holat"), {
            "fields": ("price", "is_available"),
            "classes": ["tab"],
        }),
    )

    # --- DISPLAY METODLARI ---

    @display(description="Mahsulot nomi")
    def name_display(self, obj):
        return obj.name

    @display(description="Kategoriya", label=True)
    def category_badge(self, obj):
        return obj.category.name if obj.category else "Kategoriyasiz"

    @display(description="Narxi")
    def formatted_price(self, obj):
        if obj.price:
            formatted = "{:,.0f}".format(float(obj.price)).replace(",", " ")
            return format_html('<span class="font-semibold text-gray-900">{} UZS</span>', formatted)
        return "-"

    @display(description="Holati", boolean=True)
    def availability_status(self, obj):
        return obj.is_available

    # --- DASHBOARD METRICS ---
    def get_list_display_metrics(self, request):
        from django.db.models import Avg, Max
        stats = Product.objects.aggregate(avg_price=Avg('price'), max_price=Max('price'))

        return [
            {
                "title": "Jami mahsulotlar",
                "value": Product.objects.count(),
                "icon": "inventory",
                "color": "primary",
            },
            {
                "title": "O'rtacha narx",
                "value": f"{int(stats['avg_price'] or 0):,} UZS".replace(",", " "),
                "icon": "payments",
                "color": "success",
            },
        ]

    # Queryset optimizatsiyasi
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

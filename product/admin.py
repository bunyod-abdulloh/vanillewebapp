from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_available",
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

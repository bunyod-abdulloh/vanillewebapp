from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from client.models import Banner
from product.models import Product, Category


@ensure_csrf_cookie
def home_page(request):
    # Faqat mavjud mahsulotlarni va tegishli kategoriyalarni yuklash
    active_products = Product.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    # Bazaviy URL (Telegram WebApp-da rasm yo'llari to'liq bo'lishi kerak)
    base_url = request.build_absolute_uri('/')[:-1]

    products_data = []

    banners = Banner.objects.filter(is_active=True)

    for p in active_products:
        products_data.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'cat': p.category.name.lower() if p.category else "boshqa",
            'img': f"{base_url}{p.image.url}" if p.image else f"{base_url}/static/img/no-image.png"
        })

    context = {
        'categories': categories,
        'products_list': products_data,
        'banners': banners,
    }
    return render(request, 'index.html', context)


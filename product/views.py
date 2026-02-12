from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from product.models import Product, Category

@ensure_csrf_cookie
def home_page(request):
    # Faqat mavjud mahsulotlarni va tegishli kategoriyalarni yuklash
    active_products = Product.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    # Bazaviy URL-ni aniqlaymiz (masalan: https://9e61...ngrok-free.app)
    # Bu Telegram WebApp-da rasmlar ko'rinishi uchun shart!
    base_url = request.build_absolute_uri('/')[:-1]

    products_data = []
    for p in active_products:
        products_data.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'cat': p.category.name.lower() if p.category else "boshqa",
            # Rasm yo'lini to'liq URL-ga aylantiramiz
            'img': f"{base_url}{p.image.url}" if p.image else f"{base_url}/static/img/no-image.png"
        })

    context = {
        'categories': categories,
        'products_list': products_data
    }
    return render(request, 'index.html', context)

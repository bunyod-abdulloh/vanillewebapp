import json

import requests
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Modellarni import qilish
from client.models import Client
from config.env_config import ADMIN_GROUP, BOT_TOKEN
from product.models import Product
from .models import Order, OrderItem


def send_telegram_location(chat_id, lat, lon):
    """Guruhga mijoz lokatsiyasini xarita ko'rinishida yuborish"""
    token = BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendLocation"
    payload = {
        "chat_id": chat_id,
        "latitude": float(lat),
        "longitude": float(lon)
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lokatsiya yuborishda xato: {e}")


def send_telegram_message(message):
    """Adminlar guruhiga matnli xabar yuborish"""
    token = BOT_TOKEN
    group_id = ADMIN_GROUP
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": group_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Xabar yuborishda xato: {e}")


@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')

            # 1. Mijozni topamiz
            try:
                client = Client.objects.get(telegram_id=telegram_id)
            except Client.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Mijoz topilmadi'}, status=404)

            # 2. Order yaratish
            new_order = Order.objects.create(
                client=client,
                shop=client.shop,
                comment=data.get('comment', 'Yo\'q')
            )

            items_text = ""
            total_order_sum = 0

            # 3. Savatdagi mahsulotlarni aylanamiz
            for item in data.get('items', []):
                product = Product.objects.get(id=item.get('product_id'))
                qty = int(item.get('quantity', 0))

                if qty <= 0: continue

                order_item = OrderItem.objects.create(
                    order=new_order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )
                total_order_sum += order_item.summary
                items_text += f"🔹 <b>{product.name}</b>\n   └ {qty} x {product.price:,.0f} = {order_item.summary:,.0f} so'm\n"

            # 4. Yakuniy summani saqlash
            new_order.total_price = total_order_sum
            new_order.save()

            # 5. Hisobotni tayyorlash
            client_name = getattr(client, 'full_name', 'Noma’lum')
            client_phone = getattr(client, 'phone', 'Kiritilmagan')
            branch_name = getattr(client, 'filial_name', 'Kiritilmagan')

            report = (
                f"🛍 <b>YANGI BUYURTMA #{new_order.id}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Mijoz:</b> {client_name}\n"
                f"📞 <b>Tel:</b> {client_phone}\n"
                f"🏪 <b>Restoran:</b> {client.shop.name}\n"
                f"📍 <b>Filial:</b> {branch_name}\n"                
                f"💬 <b>Izoh:</b> {new_order.comment}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{items_text}"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 <b>JAMI: {total_order_sum:,.0f} so'm</b>\n"
                f"⏰ <b>Vaqt:</b> {timezone.localtime(new_order.created_at).strftime('%H:%M | %d.%m.%Y')}"
            )

            # 6. Lokatsiyani yuborish (Client jadvalidan olingan)
            if client.latitude and client.longitude:
                send_telegram_location(ADMIN_GROUP, client.latitude, client.longitude)

            send_telegram_message(report)

            return JsonResponse({'status': 'success', 'order_id': new_order.id})

        except Exception as e:
            print(f"Xatolik: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=405)

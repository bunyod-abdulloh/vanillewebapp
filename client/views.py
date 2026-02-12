from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Shop, Client
from .serializers import ClientSerializer


# 1. HTML sahifani ko'rsatuvchi View
def anketa_page(request):
    shops = Shop.objects.all()
    return render(request, 'includes/anketa.html', {'shops': shops})


# 2. Ma'lumotni saqlovchi API View
class SaveClientView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        shop_name = request.data.get("shop_name")

        if not telegram_id:
            return Response(
                {"telegram_id": ["Telegram ID majburiy"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not shop_name:
            return Response(
                {"shop_name": ["Do‘kon nomi majburiy"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔴 1. TELEGRAM ID OLDINDAN BOR-YO‘QLIGINI TEKSHIRAMIZ
        if Client.objects.filter(telegram_id=telegram_id).exists():
            return Response(
                {
                    "telegram_id": [
                        "Siz allaqachon ro‘yxatdan o‘tgansiz"
                    ]
                },
                status=status.HTTP_409_CONFLICT
            )

        # 2. Shop topiladi yoki yaratiladi
        shop, _ = Shop.objects.get_or_create(
            name=shop_name.strip()
        )

        # 3. Client serializer
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response(
                {"status": "success", "shop_id": shop.id},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

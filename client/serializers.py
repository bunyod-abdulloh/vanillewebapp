from rest_framework import serializers
from .models import Client, Shop

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "telegram_id",
            "full_name",
            "phone",
            "filial_name",
            "latitude",
            "longitude",
        )

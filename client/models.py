from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="clients"
    )
    filial_name = models.CharField(max_length=100, verbose_name="Filial")
    telegram_id = models.BigIntegerField(null=False)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.full_name

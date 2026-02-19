from django.db import models

from client.models import Client, Shop
from product.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Buyurtma qilindi"
        CONFIRMED = "confirmed", "Tasdiqlandi"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELED = "canceled", "Bekor qilindi"

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="orders", verbose_name="Restoran")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders", verbose_name="Mijoz (filial)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name="Holati")

    # Umumiy summa Order jadvalining o'zida saqlanadi
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Umumiy summa",
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Buyurtma sanasi")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tasdiqlangan sana")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Yetkazilgan sana")
    comment = models.TextField(blank=True, verbose_name="Izoh")

    def update_total_price(self):
        """Barcha itemlar summasini qayta hisoblab, total_price ga saqlaydi"""
        total = sum(item.summary for item in self.items.all())
        self.total_price = total
        # Faqat total_price ustunini yangilash (save() rekursiya bermasligi uchun)
        Order.objects.filter(pk=self.pk).update(total_price=total)

    def __str__(self):
        return f"#{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items", verbose_name="Buyurtma")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    quantity = models.PositiveIntegerField(verbose_name="Soni")

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Bir dona narxi",
        blank=True,
        null=True
    )

    # Har bir qatorning jami summasi (quantity * price)
    summary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Jami summa",
        editable=False,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        # 1. Narxni bazadagi mahsulot narxi bilan to'ldirish
        if self.price is None:
            self.price = self.product.price

        # 2. Qator summasini hisoblash
        self.summary = self.price * self.quantity

        super().save(*args, **kwargs)

        # 3. Asosiy buyurtmaning umumiy summasini yangilash
        self.order.update_total_price()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        # Mahsulot o'chirilganda ham asosiy summani yangilab qo'yamiz
        order.update_total_price()

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

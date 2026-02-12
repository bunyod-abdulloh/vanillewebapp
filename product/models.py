from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Kategoriya"
    )
    name = models.CharField(max_length=200, verbose_name="Nomi")
    image = models.ImageField(upload_to="products/", verbose_name="Rasm")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Narxi")
    description = models.TextField(null=True, blank=True, verbose_name="Tavsifi")

    # Standart BooleanField - Admin panelda galochka bo'lib chiqadi
    is_available = models.BooleanField(
        default=True,
        verbose_name="Mavjudmi?"
    )

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name
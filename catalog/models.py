from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode


class Manufacturer(models.Model):

    name = models.CharField(max_length=200, verbose_name="Производитель")
    country = models.CharField(max_length=100, verbose_name="Страна", blank=True)

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductType(models.Model):

    name = models.CharField(max_length=100, verbose_name="Вид товара")

    class Meta:
        verbose_name = "Вид товара"
        verbose_name_plural = "Виды товаров"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=300, unique=True, verbose_name="Наименование")
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Производитель"
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Вид товара"
    )
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Фото товара",

        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    slug = models.SlugField(max_length=350, unique=True, null=False, blank=True, verbose_name="URL")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Создаем слаг из названия
            base_slug = slugify(unidecode(self.name))
            slug = base_slug
            counter = 1
            # Проверяем уникальность
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.manufacturer.name}"

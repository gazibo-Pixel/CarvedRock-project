from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.functional import cached_property
from decimal import Decimal


class ProductInStockQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(stock_count__gt=0)


class Product(models.Model):
    name = models.CharField(max_length=100)
    stock_count = models.IntegerField(help_text="How many items are currently in stock.")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(default="", blank=True)
    sku = models.CharField(verbose_name="Stock Keeping Unit", max_length=20, unique=True)
    slug = models.SlugField()
    objects = models.Manager()
    in_stock = ProductInStockQuerySet.as_manager()

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['price']
        constraints = [
             models.CheckConstraint(check=models.Q(price__gte=0),
                                    name="price_not_negative")
        ]

    def get_absolute_url(self):
        return reverse("store:product-detail", kwargs={'pk': self.id})

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    image = models.ImageField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return str(self.image)


class Category(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField('Product', related_name="categories")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

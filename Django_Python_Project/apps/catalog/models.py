from django.db import models
from django.utils.text import slugify

# class Category(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=120, unique=True)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)
#     parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
#
#     class Meta:
#         verbose_name_plural = "Categories"
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
# class Product(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     category_id = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
#     name = models.CharField(max_length=200)
#     slug = models.SlugField(max_length=220, unique=True, blank=True)
#     brand = models.CharField(max_length=120, blank=True)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     stock = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     average_rating = models.FloatField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     update_at = models.DateTimeField(auto_now_add=True)
#
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(f"{self.name}-{self.brand}")
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
# class ProductImage(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
#     image_url = models.URLField(max_length=500, blank=True)
#     image = models.ImageField(upload_to="products/")
#     s_primary = models.CharField(max_length=160, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
# TẠM CHƯA XONG
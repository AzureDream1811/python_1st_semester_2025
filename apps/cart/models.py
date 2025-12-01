from django.db import models
from django.conf import settings
from apps.products.models import Product


class Cart(models.Model):
    """Model giỏ hàng"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='Người dùng'
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name='Session Key'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'
    
    def __str__(self):
        if self.user:
            return f"Giỏ hàng của {self.user.email}"
        return f"Giỏ hàng #{self.pk}"
    
    @property
    def total_items(self):
        """Tổng số sản phẩm trong giỏ"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Tổng tiền hàng"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Tổng tiền thanh toán"""
        # Có thể thêm phí ship, giảm giá ở đây
        return self.subtotal
    
    def clear(self):
        """Xóa tất cả items trong giỏ"""
        self.items.all().delete()
    
    def merge_cart(self, session_cart):
        """Merge giỏ hàng từ session vào user cart"""
        for item in session_cart.items.all():
            existing_item = self.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        session_cart.delete()


class CartItem(models.Model):
    """Model item trong giỏ hàng"""
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Giỏ hàng'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Sản phẩm'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Số lượng')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sản phẩm trong giỏ'
        verbose_name_plural = 'Sản phẩm trong giỏ'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def price(self):
        """Giá sản phẩm"""
        return self.product.current_price
    
    @property
    def total_price(self):
        """Thành tiền"""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        # Đảm bảo số lượng không vượt quá tồn kho
        if self.quantity > self.product.stock:
            self.quantity = self.product.stock
        super().save(*args, **kwargs)

from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):
    """Model giỏ hàng"""

    user = models.ForeignKey(
        User,
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
    voucher = models.ForeignKey(
        'promotions.Voucher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='Voucher'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'

    def __str__(self):
        if self.user:
            return f"Giỏ hàng của {self.user.email}"
        return f"Giỏ hàng #{self.session_key}"

    @property
    def active_items(self):
        """Items chưa bị đánh dấu thanh toán sau"""
        return self.items.filter(saved_for_later=False)

    @property
    def saved_items(self):
        """Items đã đánh dấu thanh toán sau"""
        return self.items.filter(saved_for_later=True)

    @property
    def total_items(self):
        """Tổng số sản phẩm trong giỏ (chỉ tính active)"""
        return sum(item.quantity for item in self.active_items)

    @property
    def subtotal(self):
        """Tổng tiền hàng (chỉ tính active)"""
        return sum(item.total_price for item in self.active_items)

    @property
    def discount(self):
        """Số tiền được giảm từ voucher"""
        if not self.voucher or not self.voucher.is_valid():
            return 0

        subtotal = self.subtotal

        if subtotal < self.voucher.min_order_value:
            return 0

        if self.voucher.discount_type == 'percentage':
            discount_amount = subtotal * self.voucher.discount_value / 100
            if self.voucher.max_discount and discount_amount > self.voucher.max_discount:
                discount_amount = self.voucher.max_discount
        else:
            discount_amount = self.voucher.discount_value

        return min(discount_amount, subtotal)

    @property
    def total(self):
        """Tổng tiền thanh toán (chỉ tính active)"""
        return self.subtotal - self.discount

    def apply_voucher(self, voucher):
        """Áp dụng voucher vào giỏ hàng"""
        self.voucher = voucher
        self.save(update_fields=['voucher', 'updated_at'])

    def remove_voucher(self):
        """Xóa voucher khỏi giỏ hàng"""
        self.voucher = None
        self.save(update_fields=['voucher', 'updated_at'])

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
    saved_for_later = models.BooleanField(default=False, verbose_name='Thanh toán sau')
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
        super().save(*args, **kwargs)

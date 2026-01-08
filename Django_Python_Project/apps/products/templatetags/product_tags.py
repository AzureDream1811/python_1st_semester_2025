# apps/products/templatetags/product_tags.py

from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.filter
def currency(value):
    """Format số tiền theo định dạng VNĐ"""
    try:
        # Handle Decimal type
        if isinstance(value, Decimal):
            value = int(value)
        else:
            value = int(value)
        formatted = "{:,.0f}".format(value).replace(",", ".")
        return f"{formatted} ₫"
    except (ValueError, TypeError):
        return value


@register.filter(name='format_currency')  # ← THÊM ALIAS NÀY
def format_currency(value):
    """
    Alias for currency filter
    Format số tiền theo định dạng VNĐ: 1.000.000 ₫
    """
    return currency(value)


@register.filter
def currency_plain(value):
    """Format số tiền không có đơn vị"""
    try:
        if isinstance(value, Decimal):
            value = int(value)
        else:
            value = int(value)
        return "{:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter(name='format_price')  # ← THÊM ALIAS NÀY
def format_price(value):
    """Alias for currency_plain"""
    return currency_plain(value)


@register.simple_tag
def price_display(product):
    """Hiển thị giá sản phẩm với giá gốc và giá sale"""
    if product.sale_price and product.sale_price < product.price:
        return mark_safe(f"""
            <span class="sale-price">{currency(product.sale_price)}</span>
            <span class="original-price">{currency(product.price)}</span>
            <span class="discount-badge">-{product.discount_percent}%</span>
        """)
    return mark_safe(f'<span class="price">{currency(product.price)}</span>')


@register.filter
def star_rating(rating):
    """Hiển thị rating bằng sao"""
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return ""

    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    html = ""
    html += '<i class="bi bi-star-fill text-warning"></i>' * full_stars
    if half_star:
        html += '<i class="bi bi-star-half text-warning"></i>'
    html += '<i class="bi bi-star text-warning"></i>' * empty_stars

    return mark_safe(html)


@register.filter
def sentiment_badge(sentiment):
    """Hiển thị badge sentiment"""
    badges = {
        "positive": '<span class="badge bg-success">✓ Tích cực</span>',
        "negative": '<span class="badge bg-danger">✗ Tiêu cực</span>',
        "neutral": '<span class="badge bg-secondary">− Trung lập</span>',
    }
    return mark_safe(badges.get(sentiment, badges["neutral"]))


@register.filter
def stock_status(product):
    """Hiển thị trạng thái tồn kho"""
    if product.stock <= 0:
        return mark_safe('<span class="badge bg-danger">Hết hàng</span>')
    elif product.stock <= 5:
        return mark_safe(
            f'<span class="badge bg-warning">Còn {product.stock} sản phẩm</span>'
        )
    return mark_safe('<span class="badge bg-success">Còn hàng</span>')


# ========== THÊM CÁC FILTER UTILITY KHÁC ==========

@register.filter
def multiply(value, arg):
    """Nhân hai số"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def subtract(value, arg):
    """Trừ hai số"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Chia hai số"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def percentage(value, total):
    """Tính phần trăm"""
    try:
        if float(total) == 0:
            return 0
        return int((float(value) / float(total)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def discount_percentage(original_price, sale_price):
    """
    Tính phần trăm giảm giá
    Usage: {{ product.price|discount_percentage:product.sale_price }}
    """
    try:
        original = float(original_price)
        sale = float(sale_price)
        if original > 0 and sale < original:
            discount = ((original - sale) / original) * 100
            return int(discount)
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

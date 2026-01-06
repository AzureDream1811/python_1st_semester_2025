from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def currency(value):
    """Format số tiền theo định dạng VNĐ"""
    try:
        value = int(value)
        formatted = "{:,.0f}".format(value).replace(",", ".")
        return f"{formatted} ₫"
    except (ValueError, TypeError):
        return value


@register.filter
def currency_plain(value):
    """Format số tiền không có đơn vị"""
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.simple_tag
def price_display(product):
    """Hiển thị giá sản phẩm với giá gốc và giá sale"""
    if product.sale_price and product.sale_price < product.price:
        return mark_safe(f"""
            <span class="text-danger fw-bold">{currency(product.sale_price)}</span>
            <span class="text-muted text-decoration-line-through small">{currency(product.price)}</span>
            <span class="badge bg-danger">-{product.discount_percent}%</span>
        """)
    return mark_safe(f'<span class="fw-bold">{currency(product.price)}</span>')


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
        "positive": '<span class="badge bg-success"><i class="bi bi-emoji-smile"></i> Tích cực</span>',
        "negative": '<span class="badge bg-danger"><i class="bi bi-emoji-frown"></i> Tiêu cực</span>',
        "neutral": '<span class="badge bg-secondary"><i class="bi bi-emoji-neutral"></i> Trung lập</span>',
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

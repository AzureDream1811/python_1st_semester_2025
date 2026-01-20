from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def smart_image_url(image_field):
    """
    Returns the correct URL for an image field.
    If the stored path is already a full URL (http/https), return it directly.
    Otherwise, return the standard .url property.
    """
    if not image_field:
        return ''

    # Get the name/path stored in the field
    image_name = str(image_field.name) if hasattr(image_field, 'name') else str(image_field)

    # Check if it's already a full URL
    if image_name.startswith(('http://', 'https://')):
        return image_name

    # Otherwise return the normal URL
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return ''


@register.filter
def fix_image_url(url_string):
    """
    Fix URL string đã bị lưu sai (có /media/ prefix với external URL).
    Dùng cho CharField chứa URL như OrderItem.product_image.
    """
    if not url_string:
        return ''

    url = str(url_string)

    # Nếu URL bị lưu sai dạng "/media/https:/..." thì fix lại
    if url.startswith('/media/http'):
        # Loại bỏ /media/ prefix
        url = url[7:]  # Bỏ "/media/"
        # Fix lại https:/ thành https://
        url = url.replace('https:/', 'https://').replace('http:/', 'http://')

    # Nếu đã là URL đúng, trả về nguyên
    if url.startswith(('http://', 'https://')):
        return url

    # Nếu là path local, giữ nguyên
    return url_string


@register.filter
def currency(value):
    """Format số tiền theo định dạng VNĐ: 3.500.000₫"""
    try:
        value = int(value)
        formatted = "{:,.0f}".format(value).replace(",", ".")
        return f"{formatted}₫"
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
        return mark_safe(f'''
            <span class="text-danger fw-bold">{currency(product.sale_price)}</span>
            <span class="text-muted text-decoration-line-through small">{currency(product.price)}</span>
            <span class="badge bg-danger">-{product.discount_percent}%</span>
        ''')
    return mark_safe(f'<span class="fw-bold">{currency(product.price)}</span>')


@register.filter
def star_rating(rating):
    """Hiển thị rating bằng sao"""
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    html = ''
    html += '<i class="bi bi-star-fill text-warning"></i>' * full_stars
    if half_star:
        html += '<i class="bi bi-star-half text-warning"></i>'
    html += '<i class="bi bi-star text-warning"></i>' * empty_stars

    return mark_safe(html)


@register.filter
def sentiment_badge(sentiment):
    """Hiển thị badge sentiment với màu sắc dễ đọc"""
    badges = {
        'positive': '<span class="badge" style="background-color: #198754; color: #fff;"><i class="bi bi-emoji-smile"></i> Tích cực</span>',
        'negative': '<span class="badge" style="background-color: #dc3545; color: #fff;"><i class="bi bi-emoji-frown"></i> Tiêu cực</span>',
        'neutral': '<span class="badge" style="background-color: #6c757d; color: #fff;"><i class="bi bi-emoji-neutral"></i> Trung lập</span>',
    }
    return mark_safe(badges.get(sentiment, badges['neutral']))


@register.filter
def stock_status(product):
    """Hiển thị trạng thái tồn kho"""
    if product.stock <= 0:
        return mark_safe('<span class="badge bg-danger">Hết hàng</span>')
    elif product.stock <= 5:
        return mark_safe(f'<span class="badge bg-warning">Còn {product.stock} sản phẩm</span>')
    return mark_safe('<span class="badge bg-success">Còn hàng</span>')


@register.filter
def get_item(dictionary, key):
    """Lấy giá trị từ dictionary theo key"""
    if dictionary is None:
        return ''
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


@register.filter
def get_rating_count(product, rating):
    """Get the count of reviews with a specific rating"""
    try:
        rating = int(rating)
        if hasattr(product, 'reviews'):
            return product.reviews.filter(rating=rating, is_approved=True).count()
        return 0
    except (ValueError, TypeError):
        return 0

from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def vnd(value):
    """
    Format số tiền theo định dạng Việt Nam: 3.825.000₫
    """
    if value is None:
        return ''

    try:
        if isinstance(value, Decimal):
            value = int(value)
        else:
            value = int(float(value))

        formatted = '{:,}'.format(value).replace(',', '.')
        return f'{formatted}₫'
    except (ValueError, TypeError):
        return str(value)


@register.filter
def vnd_no_symbol(value):
    """
    Format số tiền theo định dạng Việt Nam không có ký hiệu: 3.825.000
    """
    if value is None:
        return ''

    try:
        if isinstance(value, Decimal):
            value = int(value)
        else:
            value = int(float(value))

        return '{:,}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return str(value)

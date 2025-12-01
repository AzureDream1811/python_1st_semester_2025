"""
Context processors cho catalog app
Cung cấp dữ liệu catalog cho tất cả templates
"""
from .models import Category, Tag


def catalog_context(request):
    """
    Thêm các danh mục và tags vào context cho tất cả templates
    """
    return {
        'catalog_root_categories': Category.objects.root_categories()[:6],
        'catalog_all_categories': Category.objects.active()[:10],
        'popular_tags': Tag.objects.filter(is_active=True)[:10],
    }


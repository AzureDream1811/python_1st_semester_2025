from .models import Category


def categories_context(request):
    """Context processor để hiển thị categories ở mọi trang"""
    categories = Category.objects.filter(
        is_active=True,
        parent_id=True
    ).prefetch_related('children')
    
    return {
        'nav_categories': categories
    }

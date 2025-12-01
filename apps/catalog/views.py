from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Category, Tag


def category_list(request):
    """Hiển thị danh sách tất cả danh mục"""
    categories = Category.objects.root_categories().prefetch_related('children')

    context = {
        'categories': categories,
        'page_title': 'Danh mục sản phẩm',
    }
    return render(request, 'catalog/category_list.html', context)


def category_detail(request, slug):
    """Hiển thị chi tiết danh mục và sản phẩm thuộc danh mục"""
    from apps.products.models import Product

    category = get_object_or_404(Category, slug=slug, is_active=True)

    # Lấy tất cả danh mục con
    child_categories = category.get_all_children()
    all_categories = [category] + child_categories

    # Lấy sản phẩm trong danh mục và danh mục con
    products = Product.objects.filter(
        category__in=all_categories,
        is_active=True
    ).select_related('category', 'brand').order_by('-created_at')

    # Lọc theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sắp xếp
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'price': 'price',
        '-price': '-price',
        '-created_at': '-created_at',
        '-views': '-views',
    }
    if sort_by in valid_sorts:
        products = products.order_by(valid_sorts[sort_by])

    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'child_categories': category.children.filter(is_active=True),
        'products': page_obj,
        'page_obj': page_obj,
        'page_title': category.name,
        'meta_description': category.meta_description or category.description,
    }
    return render(request, 'catalog/category_detail.html', context)


def tag_list(request):
    """Hiển thị danh sách tất cả tags"""
    tags = Tag.objects.filter(is_active=True).annotate(
        product_count=Count('products')
    ).order_by('-product_count', 'name')

    context = {
        'tags': tags,
        'page_title': 'Thẻ tag sản phẩm',
    }
    return render(request, 'catalog/tag_list.html', context)


def tag_detail(request, slug):
    """Hiển thị sản phẩm theo tag"""
    from apps.products.models import Product

    tag = get_object_or_404(Tag, slug=slug, is_active=True)

    # Lấy sản phẩm có tag này
    products = Product.objects.filter(
        tags=tag,
        is_active=True
    ).select_related('category', 'brand').order_by('-created_at')

    # Sắp xếp
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'price': 'price',
        '-price': '-price',
        '-created_at': '-created_at',
    }
    if sort_by in valid_sorts:
        products = products.order_by(valid_sorts[sort_by])

    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'products': page_obj,
        'page_obj': page_obj,
        'page_title': f'Tag: {tag.name}',
    }
    return render(request, 'catalog/tag_detail.html', context)


def category_tree(request):
    """Hiển thị cây danh mục đầy đủ"""
    root_categories = Category.objects.root_categories().prefetch_related(
        'children',
        'children__children'
    )

    context = {
        'root_categories': root_categories,
        'page_title': 'Cấu trúc danh mục',
    }
    return render(request, 'catalog/category_tree.html', context)


def search_catalog(request):
    """Tìm kiếm trong catalog"""
    query = request.GET.get('q', '')

    categories = Category.objects.none()
    tags = Tag.objects.none()

    if query:
        # Tìm kiếm danh mục
        categories = Category.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )

        # Tìm kiếm tags
        tags = Tag.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        )

    context = {
        'query': query,
        'categories': categories,
        'tags': tags,
        'page_title': f'Tìm kiếm: {query}',
    }
    return render(request, 'catalog/search.html', context)

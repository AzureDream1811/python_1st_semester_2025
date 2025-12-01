from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface cho Category"""

    list_display = [
        'name',
        'get_level_display',
        'parent',
        'order',
        'is_active',
        'get_products_count',
        'image_preview',
        'created_at'
    ]
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Hình ảnh & Icon', {
            'fields': ('image', 'icon')
        }),
        ('Hiển thị', {
            'fields': ('order', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    def get_level_display(self, obj):
        """Hiển thị cấp độ của danh mục"""
        return '—' * obj.level + ' Level ' + str(obj.level)
    get_level_display.short_description = 'Cấp độ'

    def image_preview(self, obj):
        """Hiển thị preview hình ảnh"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Hình ảnh'

    def get_products_count(self, obj):
        """Hiển thị số lượng sản phẩm"""
        count = obj.get_products_count()
        all_count = obj.get_all_products_count()
        if count != all_count:
            return format_html(
                '<span style="color: #007bff;">{}</span> (<span style="color: #6c757d;">tổng: {}</span>)',
                count,
                all_count
            )
        return count
    get_products_count.short_description = 'Số sản phẩm'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface cho Tag"""

    list_display = [
        'name',
        'color_preview',
        'get_products_count',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Hiển thị', {
            'fields': ('color', 'is_active')
        }),
    )

    def color_preview(self, obj):
        """Hiển thị màu của tag"""
        return format_html(
            '<span style="display:inline-block; width:20px; height:20px; '
            'background-color:{}; border:1px solid #ddd; border-radius:3px; '
            'vertical-align:middle;"></span> {}',
            obj.color,
            obj.color
        )
    color_preview.short_description = 'Màu sắc'

    def get_products_count(self, obj):
        """Hiển thị số lượng sản phẩm"""
        count = obj.get_products_count()
        return format_html(
            '<span style="color: #007bff;">{}</span>',
            count
        )
    get_products_count.short_description = 'Số sản phẩm'


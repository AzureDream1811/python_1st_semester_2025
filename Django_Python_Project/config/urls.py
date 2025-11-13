from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('apps.catalog.urls')),      # trang chủ, danh mục, tìm kiếm nếu cần
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('reviews/', include('apps.reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

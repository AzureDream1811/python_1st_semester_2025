"""
URL configuration for E-commerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Import admin config để customize admin site
import apps.admin_config  # noqa
import apps.admin_dashboard.admin  # noqa

urlpatterns = [
    # Redirect /admin/ to /admin-dashboard/
    path('admin/', RedirectView.as_view(url='/admin-dashboard/', permanent=False), name='admin_redirect'),

    # Custom Admin Dashboard Panel
    path('admin-dashboard/', include('apps.admin_dashboard.urls', namespace='admin_dashboard')),

    # Django Allauth for Social Login (Google, Facebook)
    path('accounts/social/', include('allauth.urls')),

    # Main app URLs
    path('', include('apps.products.urls', namespace='products')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('promotions/', include('apps.promotions.urls', namespace='promotions')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('search/', include('apps.search.urls', namespace='search')),
    path('shipping/', include('apps.shipping.urls', namespace='shipping')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('recommendations/', include('apps.recommendations.urls', namespace='recommendations')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'apps.products.views.error_404'
handler500 = 'apps.products.views.error_500'
handler403 = 'apps.products.views.error_403'

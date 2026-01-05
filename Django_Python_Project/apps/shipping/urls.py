from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('calculate/', views.calculate_shipping, name='calculate'),
    path('track/<str:tracking_code>/', views.track_shipment, name='track'),
    path('provinces/', views.get_provinces, name='provinces'),
    path('districts/<int:province_id>/', views.get_districts, name='districts'),
    path('wards/<int:district_id>/', views.get_wards, name='wards'),
]

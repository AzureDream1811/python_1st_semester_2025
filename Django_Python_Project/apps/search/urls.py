from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_products, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('suggestions/', views.search_suggestions, name='suggestions'),
]

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Danh mục
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category-tree/', views.category_tree, name='category_tree'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),

    # Tìm kiếm
    path('search/', views.search_catalog, name='search'),
]


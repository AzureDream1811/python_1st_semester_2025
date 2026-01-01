# apps/accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    # nhập email
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # thông báo đã gửi
    path('forgot-password/done/', views.password_reset_done, name='password_reset_done'),

    # click link trong email -> nhập mật khẩu mới
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/reset/done/',
        ),
        name='password_reset_confirm',
    ),

    # hoàn tất
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.account_dashboard, name='dashboard'),

    # Address management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/create/', views.address_create, name='address_create'),
    path('addresses/<int:address_id>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:address_id>/set-default/', views.address_set_default, name='address_set_default'),

    # Card management
    path('cards/', views.card_list, name='card_list'),
    path('cards/create/', views.card_create, name='card_create'),
    path('cards/<int:card_id>/delete/', views.card_delete, name='card_delete'),
    path('cards/<int:card_id>/set-default/', views.card_set_default, name='card_set_default'),

    # API endpoints
    path('api/provinces/', views.api_provinces, name='api_provinces'),
    path('api/districts/<str:province_code>/', views.api_districts, name='api_districts'),
    path('api/wards/<str:district_code>/', views.api_wards, name='api_wards'),
    path('api/validate-card/', views.api_validate_card, name='api_validate_card'),

    # Social login API endpoints
    path('api/check-email/', views.check_email_api, name='api_check_email'),
    path('api/social-register/', views.social_register_api, name='api_social_register'),
    path('api/social-login/', views.social_login_api, name='api_social_login'),
]

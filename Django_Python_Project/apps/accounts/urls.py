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
]

"""
Decorators và Mixins cho Admin Dashboard
"""
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


def staff_required(view_func):
    """Decorator yêu cầu user phải là staff"""

    def check_staff(user):
        return user.is_authenticated and user.is_staff

    decorated_view = user_passes_test(
        check_staff,
        login_url='accounts:login',
        redirect_field_name='next'
    )(view_func)
    return decorated_view


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin yêu cầu user phải là staff cho class-based views"""
    login_url = 'accounts:login'

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Bạn không có quyền truy cập trang này.')
            return redirect('products:home')
        return super().handle_no_permission()

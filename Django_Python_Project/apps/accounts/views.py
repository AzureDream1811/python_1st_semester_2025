from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


def register(request):
    """Đăng ký tài khoản mới"""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Đăng nhập"""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Merge session cart vào user cart
            from apps.cart.views import merge_session_cart
            merge_session_cart(request)

            # Remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            messages.success(request, f'Chào mừng {user.first_name}!')

            # Redirect to next or home
            next_url = request.GET.get('next', 'products:home')
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Đăng xuất"""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('products:home')

def forgot_password(request):
    """Nhập email để gửi link đặt lại mật khẩu."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # form.save() sẽ:
            # - tìm user theo email
            # - tạo token reset
            # - gửi email theo template_name
            # Nếu email không tồn tại: không gửi, nhưng vẫn trả về như thành công (tránh lộ tài khoản).
            form.save(
                request=request,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                email_template_name='accounts/password_reset_email.html',
                subject_template_name='accounts/password_reset_subject.txt',
            )
            messages.success(request, 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu.')
            return redirect('accounts:password_reset_done')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def password_reset_done(request):
    """Trang thông báo đã gửi email reset."""
    return render(request, 'accounts/password_reset_done.html')

@login_required
def profile(request):
    """Xem và cập nhật hồ sơ"""
    # Đảm bảo user có profile
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user, email=request.user.email)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    # Load order history
    orders = request.user.orders.all().order_by('-created_at')[:5]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)

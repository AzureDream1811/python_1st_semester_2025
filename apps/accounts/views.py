from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import (
    UserRegistrationForm, UserLoginForm, UserUpdateForm,
    CustomPasswordChangeForm, AddressForm
)
from .models import User, Address


def register_view(request):
    """View đăng ký tài khoản"""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký tài khoản thành công!')
            return redirect('products:home')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """View đăng nhập"""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Remember me functionality
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            messages.success(request, f'Chào mừng {user.get_full_name()} quay trở lại!')
            
            # Redirect to next page if exists
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('products:home')
        else:
            messages.error(request, 'Email hoặc mật khẩu không đúng.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """View đăng xuất"""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất thành công.')
    return redirect('products:home')


@login_required
def profile_view(request):
    """View xem profile"""
    return render(request, 'accounts/profile.html')


@login_required
def profile_update_view(request):
    """View cập nhật profile"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})


@login_required
def change_password_view(request):
    """View đổi mật khẩu"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


# Address Views
@login_required
def address_list_view(request):
    """View danh sách địa chỉ"""
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_create_view(request):
    """View thêm địa chỉ mới"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Thêm địa chỉ thành công!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Thêm địa chỉ mới'})


@login_required
def address_update_view(request, pk):
    """View cập nhật địa chỉ"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật địa chỉ thành công!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Cập nhật địa chỉ'})


@login_required
def address_delete_view(request, pk):
    """View xóa địa chỉ"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Xóa địa chỉ thành công!')
        return redirect('accounts:address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def set_default_address_view(request, pk):
    """View đặt địa chỉ mặc định"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    # Bỏ mặc định các địa chỉ khác
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Đặt địa chỉ này làm mặc định
    address.is_default = True
    address.save()
    
    messages.success(request, 'Đã đặt làm địa chỉ mặc định!')
    return redirect('accounts:address_list')

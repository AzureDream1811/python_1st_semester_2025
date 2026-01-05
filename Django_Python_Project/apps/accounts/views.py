import json
import re

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Address, SavedCard
from .services.address_service import AddressService
from .services.social_auth_service import SocialAuthService
from apps.orders.models import Order
from apps.payments.services.card_service import CardValidator


# ============== AUTH VIEWS ==============

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

            # Lưu session key cũ trước khi login
            old_session_key = request.session.session_key

            login(request, user)

            # Merge session cart vào user cart
            from apps.cart.views import merge_session_cart_with_key
            merge_session_cart_with_key(request, old_session_key)

            # Remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            messages.success(request, f'Chào mừng {user.first_name}!')

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


# ============== PROFILE VIEWS ==============

@login_required
def profile(request):
    """Xem và cập nhật hồ sơ"""
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

    orders = request.user.orders.all().order_by('-created_at')[:5]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def account_dashboard(request):
    """Dashboard tổng quan tài khoản"""
    user = request.user

    total_orders = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    completed_orders = Order.objects.filter(user=user, status='delivered').count()
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]

    voucher_count = 0
    expiring_vouchers = []
    try:
        from apps.promotions.models import UserVoucher
        voucher_count = UserVoucher.objects.filter(user=user, is_used=False).count()

        expiring_date = timezone.now() + timedelta(days=7)
        expiring_vouchers = UserVoucher.objects.filter(
            user=user,
            is_used=False,
            voucher__end_date__lte=expiring_date,
            voucher__end_date__gte=timezone.now()
        ).select_related('voucher')[:5]
    except Exception:
        pass

    wishlist_count = 0
    try:
        from apps.products.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=user).count()
    except Exception:
        pass

    address_count = Address.objects.filter(user=user).count()
    card_count = SavedCard.objects.filter(user=user).count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_orders': recent_orders,
        'voucher_count': voucher_count,
        'expiring_vouchers': expiring_vouchers,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
        'card_count': card_count,
    }
    return render(request, 'accounts/dashboard.html', context)


# ============== ADDRESS VIEWS ==============

@login_required
def address_list(request):
    """Danh sách địa chỉ đã lưu"""
    addresses = Address.objects.filter(user=request.user)

    context = {
        'addresses': addresses,
        'active_tab': 'addresses'
    }
    return render(request, 'accounts/profile_addresses.html', context)


@login_required
def address_create(request):
    """Thêm địa chỉ mới"""
    if request.method == 'POST':
        data = request.POST

        required_fields = ['full_name', 'phone', 'address', 'province', 'province_code',
                           'district', 'district_code']
        for field in required_fields:
            if not data.get(field):
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('accounts:address_create')

        is_default = data.get('is_default') == 'on'

        Address.objects.create(
            user=request.user,
            full_name=data['full_name'],
            phone=data['phone'],
            address=data['address'],
            province=data['province'],
            province_code=data['province_code'],
            district=data['district'],
            district_code=data['district_code'],
            ward=data.get('ward', ''),
            ward_code=data.get('ward_code', ''),
            is_default=is_default
        )

        messages.success(request, 'Thêm địa chỉ thành công!')
        return redirect('accounts:address_list')

    provinces = AddressService.get_provinces()

    context = {
        'provinces': provinces,
        'active_tab': 'addresses'
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
def address_edit(request, address_id):
    """Sửa địa chỉ"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        messages.error(request, 'Địa chỉ không tồn tại')
        return redirect('accounts:address_list')

    if request.method == 'POST':
        data = request.POST

        address.full_name = data.get('full_name', address.full_name)
        address.phone = data.get('phone', address.phone)
        address.address = data.get('address', address.address)
        address.province = data.get('province', address.province)
        address.province_code = data.get('province_code', address.province_code)
        address.district = data.get('district', address.district)
        address.district_code = data.get('district_code', address.district_code)
        address.ward = data.get('ward', address.ward)
        address.ward_code = data.get('ward_code', address.ward_code)
        address.is_default = data.get('is_default') == 'on'

        address.save()

        messages.success(request, 'Cập nhật địa chỉ thành công!')
        return redirect('accounts:address_list')

    provinces = AddressService.get_provinces()
    districts = AddressService.get_districts(address.province_code) if address.province_code else []
    wards = AddressService.get_wards(address.district_code) if address.district_code else []

    context = {
        'address': address,
        'provinces': provinces,
        'districts': districts,
        'wards': wards,
        'active_tab': 'addresses',
        'is_edit': True
    }
    return render(request, 'accounts/address_form.html', context)


@login_required
@require_POST
def address_delete(request, address_id):
    """Xóa địa chỉ"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Xóa địa chỉ thành công!')
    except Address.DoesNotExist:
        messages.error(request, 'Địa chỉ không tồn tại')

    return redirect('accounts:address_list')


@login_required
@require_POST
def address_set_default(request, address_id):
    """Đặt địa chỉ mặc định"""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.is_default = True
        address.save()
        messages.success(request, 'Đã đặt làm địa chỉ mặc định!')
    except Address.DoesNotExist:
        messages.error(request, 'Địa chỉ không tồn tại')

    return redirect('accounts:address_list')


# ============== ADDRESS API VIEWS ==============

@require_GET
def api_provinces(request):
    """API lấy danh sách tỉnh/thành phố"""
    provinces = AddressService.get_provinces()
    return JsonResponse({'provinces': provinces})


@require_GET
def api_districts(request, province_code):
    """API lấy danh sách quận/huyện"""
    districts = AddressService.get_districts(province_code)
    return JsonResponse({'districts': districts})


@require_GET
def api_wards(request, district_code):
    """API lấy danh sách phường/xã"""
    wards = AddressService.get_wards(district_code)
    return JsonResponse({'wards': wards})


# ============== SAVED CARD VIEWS ==============

@login_required
def card_list(request):
    """Danh sách thẻ đã lưu"""
    cards = SavedCard.objects.filter(user=request.user)

    context = {
        'cards': cards,
        'active_tab': 'cards'
    }
    return render(request, 'accounts/profile_cards.html', context)


@login_required
def card_create(request):
    """Thêm thẻ mới"""
    if request.method == 'POST':
        data = request.POST

        card_number = data.get('card_number', '').replace(' ', '').replace('-', '')
        expiry_month = int(data.get('expiry_month', 0))
        expiry_year = int(data.get('expiry_year', 0))
        cvv = data.get('cvv', '')
        cardholder_name = data.get('cardholder_name', '').strip().upper()

        validation = CardValidator.validate_card(
            card_number=card_number,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cvv=cvv,
            cardholder_name=cardholder_name
        )

        if not validation['valid']:
            for error in validation['errors']:
                messages.error(request, error)
            return redirect('accounts:card_create')

        last_four = CardValidator.get_last_four(card_number)
        existing = SavedCard.objects.filter(
            user=request.user,
            last_four=last_four,
            card_type=validation['card_type']
        ).exists()

        if existing:
            messages.error(request, 'Thẻ này đã được lưu trước đó')
            return redirect('accounts:card_create')

        is_default = data.get('is_default') == 'on'

        SavedCard.objects.create(
            user=request.user,
            card_type=validation['card_type'],
            masked_number=validation['masked_number'],
            last_four=validation['last_four'],
            cardholder_name=cardholder_name,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            is_default=is_default
        )

        messages.success(request, 'Thêm thẻ thành công!')
        return redirect('accounts:card_list')

    context = {
        'active_tab': 'cards'
    }
    return render(request, 'accounts/card_form.html', context)


@login_required
@require_POST
def card_delete(request, card_id):
    """Xóa thẻ"""
    try:
        card = SavedCard.objects.get(id=card_id, user=request.user)
        card.delete()
        messages.success(request, 'Xóa thẻ thành công!')
    except SavedCard.DoesNotExist:
        messages.error(request, 'Thẻ không tồn tại')

    return redirect('accounts:card_list')


@login_required
@require_POST
def card_set_default(request, card_id):
    """Đặt thẻ mặc định"""
    try:
        card = SavedCard.objects.get(id=card_id, user=request.user)
        card.is_default = True
        card.save()
        messages.success(request, 'Đã đặt làm thẻ mặc định!')
    except SavedCard.DoesNotExist:
        messages.error(request, 'Thẻ không tồn tại')

    return redirect('accounts:card_list')


# ============== CARD VALIDATION API ==============

@require_POST
def api_validate_card(request):
    """API xác thực thẻ real-time"""
    try:
        data = json.loads(request.body)
        card_number = data.get('card_number', '')

        card_type = CardValidator.detect_card_type(card_number)
        clean_number = card_number.replace(' ', '').replace('-', '')
        is_valid_luhn = CardValidator.validate_luhn(card_number) if len(clean_number) >= 13 else None

        return JsonResponse({
            'card_type': card_type,
            'is_valid': is_valid_luhn
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============== SOCIAL LOGIN API ENDPOINTS ==============

@method_decorator(csrf_exempt, name='dispatch')
class CheckEmailAPIView(View):
    """API endpoint kiểm tra email đã tồn tại chưa"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()

            if not email:
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Email không được để trống'
                }, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Định dạng email không hợp lệ'
                }, status=400)

            result = SocialAuthService.check_email_exists(email)

            return JsonResponse({
                'exists': result['exists'],
                'has_social': result['has_social'],
                'providers': result['providers']
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'invalid_json',
                'message': 'Dữ liệu JSON không hợp lệ'
            }, status=400)
        except Exception:
            return JsonResponse({
                'error': 'server_error',
                'message': 'Đã có lỗi xảy ra'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SocialRegisterAPIView(View):
    """API endpoint đăng ký tài khoản qua social"""

    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data.get('email', '').strip()
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            phone = data.get('phone', '').strip()
            provider = data.get('provider', '').strip()

            if not all([email, first_name, last_name, provider]):
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Vui lòng điền đầy đủ thông tin bắt buộc',
                    'errors': {
                        'email': 'Email không được để trống' if not email else None,
                        'first_name': 'Tên không được để trống' if not first_name else None,
                        'last_name': 'Họ không được để trống' if not last_name else None,
                        'provider': 'Provider không được để trống' if not provider else None,
                    }
                }, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Định dạng email không hợp lệ'
                }, status=400)

            if phone:
                phone_pattern = r'^(0|\+84)[0-9]{9,10}$'
                if not re.match(phone_pattern, phone):
                    return JsonResponse({
                        'error': 'validation_error',
                        'message': 'Số điện thoại không đúng định dạng Việt Nam',
                        'errors': {
                            'phone': 'Số điện thoại phải có định dạng: 0xxxxxxxxx hoặc +84xxxxxxxxx'
                        }
                    }, status=400)

            result = SocialAuthService.create_social_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                provider=provider
            )

            if not result['success']:
                return JsonResponse({
                    'error': 'registration_failed',
                    'message': result['error']
                }, status=400)

            login_result = SocialAuthService.login_social_user(
                request=request,
                email=email,
                provider=provider
            )

            if not login_result['success']:
                return JsonResponse({
                    'error': 'login_failed',
                    'message': login_result['error']
                }, status=400)

            return JsonResponse({
                'success': True,
                'message': 'Đăng ký và đăng nhập thành công',
                'redirect_url': login_result['redirect_url'],
                'user': {
                    'id': result['user'].id,
                    'email': result['user'].email,
                    'first_name': result['user'].first_name,
                    'last_name': result['user'].last_name
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'invalid_json',
                'message': 'Dữ liệu JSON không hợp lệ'
            }, status=400)
        except Exception:
            return JsonResponse({
                'error': 'server_error',
                'message': 'Đã có lỗi xảy ra'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SocialLoginAPIView(View):
    """API endpoint đăng nhập qua social"""

    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data.get('email', '').strip()
            provider = data.get('provider', '').strip()

            if not email or not provider:
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Email và provider không được để trống'
                }, status=400)

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({
                    'error': 'validation_error',
                    'message': 'Định dạng email không hợp lệ'
                }, status=400)

            result = SocialAuthService.login_social_user(
                request=request,
                email=email,
                provider=provider
            )

            if not result['success']:
                return JsonResponse({
                    'error': 'login_failed',
                    'message': result['error']
                }, status=400)

            return JsonResponse({
                'success': True,
                'message': 'Đăng nhập thành công',
                'redirect_url': result['redirect_url'],
                'user': {
                    'id': result['user'].id,
                    'email': result['user'].email,
                    'first_name': result['user'].first_name,
                    'last_name': result['user'].last_name
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'invalid_json',
                'message': 'Dữ liệu JSON không hợp lệ'
            }, status=400)
        except Exception:
            return JsonResponse({
                'error': 'server_error',
                'message': 'Đã có lỗi xảy ra'
            }, status=500)


# Function-based views for URL routing
check_email_api = CheckEmailAPIView.as_view()
social_register_api = SocialRegisterAPIView.as_view()
social_login_api = SocialLoginAPIView.as_view()

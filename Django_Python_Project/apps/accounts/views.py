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

            # LƯU SESSION KEY CŨ TRƯỚC KHI LOGIN
            old_session_key = request.session.session_key

            login(request, user)

            # Merge session cart vào user cart (sử dụng old_session_key)
            from apps.cart.views import merge_session_cart_with_key
            merge_session_cart_with_key(request, old_session_key)

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


from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import json

from .models import Address, SavedCard
from .services.address_service import AddressService
from apps.payments.services.card_service import CardValidator


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

        # Validate required fields
        required_fields = ['full_name', 'phone', 'address', 'province', 'province_code',
                           'district', 'district_code']
        for field in required_fields:
            if not data.get(field):
                messages.error(request, f'Vui lòng điền đầy đủ thông tin')
                return redirect('accounts:address_create')

        # Tạo địa chỉ mới
        is_default = data.get('is_default') == 'on'

        address = Address.objects.create(
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

    # GET - hiển thị form
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

    # GET - hiển thị form với dữ liệu hiện tại
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
        address.save()  # save() sẽ tự động unset các địa chỉ khác
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

        # Validate thẻ
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

        # Kiểm tra thẻ đã tồn tại chưa
        last_four = CardValidator.get_last_four(card_number)
        existing = SavedCard.objects.filter(
            user=request.user,
            last_four=last_four,
            card_type=validation['card_type']
        ).exists()

        if existing:
            messages.error(request, 'Thẻ này đã được lưu trước đó')
            return redirect('accounts:card_create')

        # Lưu thẻ
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

    # GET - hiển thị form
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
        card.save()  # save() sẽ tự động unset các thẻ khác
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

        # Chỉ detect card type
        card_type = CardValidator.detect_card_type(card_number)
        is_valid_luhn = CardValidator.validate_luhn(card_number) if len(
            card_number.replace(' ', '').replace('-', '')) >= 13 else None

        return JsonResponse({
            'card_type': card_type,
            'is_valid': is_valid_luhn
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============== ACCOUNT DASHBOARD VIEW ==============

from datetime import timedelta
from django.utils import timezone
from apps.orders.models import Order


@login_required
def account_dashboard(request):
    """Dashboard tổng quan tài khoản"""
    user = request.user

    # Order statistics
    total_orders = Order.objects.filter(user=user).count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    completed_orders = Order.objects.filter(user=user, status='delivered').count()
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]

    # Loyalty statistics
    loyalty_points = 0
    loyalty_tier = None
    try:
        if hasattr(user, 'loyalty_account'):
            loyalty_account = user.loyalty_account
            loyalty_points = loyalty_account.points
            loyalty_tier = loyalty_account.tier
    except Exception:
        pass

    # Voucher statistics
    voucher_count = 0
    expiring_vouchers = []
    try:
        from apps.promotions.models import UserVoucher
        voucher_count = UserVoucher.objects.filter(
            user=user, is_used=False
        ).count()

        # Vouchers expiring within 7 days
        expiring_date = timezone.now() + timedelta(days=7)
        expiring_vouchers = UserVoucher.objects.filter(
            user=user,
            is_used=False,
            voucher__end_date__lte=expiring_date,
            voucher__end_date__gte=timezone.now()
        ).select_related('voucher')[:5]
    except Exception:
        pass

    # Wishlist count
    wishlist_count = 0
    try:
        from apps.products.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=user).count()
    except Exception:
        pass

    # Address count
    address_count = Address.objects.filter(user=user).count()

    # Saved cards count
    card_count = SavedCard.objects.filter(user=user).count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_orders': recent_orders,
        'loyalty_points': loyalty_points,
        'loyalty_tier': loyalty_tier,
        'voucher_count': voucher_count,
        'expiring_vouchers': expiring_vouchers,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
        'card_count': card_count,
    }
    return render(request, 'accounts/dashboard.html', context)

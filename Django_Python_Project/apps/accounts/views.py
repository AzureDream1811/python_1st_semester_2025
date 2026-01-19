import json
import re

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model

User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm
from .models import Profile, Address, SavedCard, UserSession, LoginHistory
from .services.address_service import AddressService
from .services.social_auth_service import SocialAuthService
from .decorators import rate_limit_class, require_origin_class
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

    google_client_id = settings.GOOGLE_CLIENT_ID
    return render(request, 'accounts/register.html', {
        'form': form,
        'google_client_id': google_client_id
    })


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

            # Create session and login history
            create_user_session(request, user)
            create_login_history(request, user, 'success', 'email')

            messages.success(request, f'Chào mừng {user.first_name}!')

            next_url = request.GET.get('next', 'products:home')
            return redirect(next_url)
        else:
            # Log failed login attempt
            email = request.POST.get('username', '')
            try:
                failed_user = User.objects.get(email__iexact=email)
                create_login_history(request, failed_user, 'failed', 'email')
            except User.DoesNotExist:
                pass
    else:
        form = UserLoginForm()

    google_client_id = settings.GOOGLE_CLIENT_ID
    return render(request, 'accounts/login.html', {
        'form': form,
        'google_client_id': google_client_id
    })


def logout_view(request):
    """Đăng xuất"""
    # Delete user session
    if request.user.is_authenticated:
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(user=request.user, session_key=session_key).delete()

    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('products:home')


def forgot_password(request):
    """Nhập email để gửi link đặt lại mật khẩu."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Vui lòng nhập địa chỉ email.')
            return render(request, 'accounts/forgot_password.html', {'form': PasswordResetForm()})

        user_exists = User.objects.filter(email__iexact=email).exists()

        if not user_exists:
            messages.error(request,
                           'Email này chưa được đăng ký trong hệ thống. Vui lòng kiểm tra lại hoặc tạo tài khoản mới.')
            return render(request, 'accounts/forgot_password.html', {'form': PasswordResetForm(request.POST)})

        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                email_template_name='accounts/password_reset_email.html',
                subject_template_name='accounts/password_reset_subject.txt',
            )
            messages.success(request, 'Chúng tôi đã gửi liên kết đặt lại mật khẩu đến email của bạn.')
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

    is_social = getattr(request.user.profile, 'is_social_account', False)

    if request.method == 'POST':
        # Handle avatar upload separately with validation
        if request.POST.get('avatar_upload') and request.FILES.get('avatar'):
            avatar = request.FILES['avatar']

            # Validate file size (5MB max)
            if avatar.size > 5 * 1024 * 1024:
                messages.error(request, 'Ảnh đại diện không được vượt quá 5MB.')
                return redirect('accounts:profile')

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(avatar, 'content_type') and avatar.content_type not in allowed_types:
                messages.error(request, 'Chỉ chấp nhận định dạng JPG, PNG hoặc WebP.')
                return redirect('accounts:profile')

            request.user.profile.avatar = avatar
            request.user.profile.save()
            messages.success(request, 'Cập nhật ảnh đại diện thành công!')
            return redirect('accounts:profile')

        user_form = UserUpdateForm(request.POST, instance=request.user, is_social_account=is_social)
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
        user_form = UserUpdateForm(instance=request.user, is_social_account=is_social)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    # Get orders
    orders = request.user.orders.all().order_by('-created_at')[:5]

    # Get reviews
    reviews = []
    try:
        from apps.reviews.models import Review
        reviews = Review.objects.filter(user=request.user).select_related('product').order_by('-created_at')[:10]
    except Exception:
        pass

    # Get wishlist items
    wishlist_items = []
    try:
        from apps.products.models import Wishlist
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-created_at')[
            :10]
    except Exception:
        pass

    # Get addresses
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')[:5]

    # Get saved cards
    saved_cards = SavedCard.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    # Get vouchers (public vouchers that are still valid)
    vouchers = []
    try:
        from apps.promotions.models import Voucher
        vouchers = Voucher.objects.filter(
            valid_until__gte=timezone.now(),
            is_active=True
        ).order_by('-created_at')[:6]
    except Exception:
        pass

    # Get sessions
    sessions = UserSession.objects.filter(user=request.user).order_by('-last_activity')[:10]
    current_session_key = request.session.session_key
    for session in sessions:
        if session.session_key == current_session_key:
            session.is_current = True
            session.save(update_fields=['is_current'])

    # Get login history
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:20]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
        'reviews': reviews,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
        'cards': saved_cards,
        'vouchers': vouchers,
        'sessions': sessions,
        'login_history': login_history,
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
        errors = []

        # Validate full_name
        full_name = data.get('full_name', '').strip()
        if not full_name:
            errors.append('Vui lòng nhập họ tên người nhận')
        elif len(full_name) < 4:
            errors.append('Họ tên phải có ít nhất 4 ký tự')
        elif len(full_name.split()) < 2:
            errors.append('Vui lòng nhập đầy đủ họ và tên')

        # Validate phone
        phone = data.get('phone', '').strip().replace(' ', '')
        import re
        phone_pattern = re.compile(r'^(0|\+84)[0-9]{9,10}$')
        if not phone:
            errors.append('Vui lòng nhập số điện thoại')
        elif not phone_pattern.match(phone):
            errors.append('Số điện thoại không hợp lệ (VD: 0912345678)')

        # Validate address
        address_detail = data.get('address', '').strip()
        if not address_detail:
            errors.append('Vui lòng nhập địa chỉ chi tiết')
        elif len(address_detail) < 5:
            errors.append('Địa chỉ phải có ít nhất 5 ký tự')

        # Validate province
        province_code = data.get('province_code', '').strip()
        province_name = data.get('province', '').strip()
        if not province_code or not province_name:
            errors.append('Vui lòng chọn Tỉnh/Thành phố')
        else:
            # Verify province exists
            provinces = AddressService.get_provinces()
            if not any(p['code'] == province_code for p in provinces):
                errors.append('Tỉnh/Thành phố không hợp lệ')

        # Validate district
        district_code = data.get('district_code', '').strip()
        district_name = data.get('district', '').strip()
        if not district_code or not district_name:
            errors.append('Vui lòng chọn Quận/Huyện')
        elif province_code:
            # Verify district belongs to province
            districts = AddressService.get_districts(province_code)
            if not any(d['code'] == district_code for d in districts):
                errors.append('Quận/Huyện không thuộc Tỉnh/Thành phố đã chọn')

        # Validate ward (optional but verify if provided)
        ward_code = data.get('ward_code', '').strip()
        ward_name = data.get('ward', '').strip()
        if ward_code and district_code:
            wards = AddressService.get_wards(district_code)
            if not any(w['code'] == ward_code for w in wards):
                errors.append('Phường/Xã không thuộc Quận/Huyện đã chọn')

        if errors:
            for error in errors:
                messages.error(request, error)
            provinces = AddressService.get_provinces()
            districts = AddressService.get_districts(province_code) if province_code else []
            wards = AddressService.get_wards(district_code) if district_code else []
            return render(request, 'accounts/address_form.html', {
                'provinces': provinces,
                'districts': districts,
                'wards': wards,
                'active_tab': 'addresses',
                'address': type('obj', (object,), {
                    'full_name': full_name,
                    'phone': phone,
                    'address': address_detail,
                    'province': province_name,
                    'province_code': province_code,
                    'district': district_name,
                    'district_code': district_code,
                    'ward': ward_name,
                    'ward_code': ward_code,
                    'is_default': data.get('is_default') == 'on'
                })()
            })

        is_default = data.get('is_default') == 'on'

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address_detail,
            province=province_name,
            province_code=province_code,
            district=district_name,
            district_code=district_code,
            ward=ward_name,
            ward_code=ward_code,
            is_default=is_default
        )

        messages.success(request, 'Thêm địa chỉ thành công!')
        return HttpResponseRedirect(reverse('accounts:profile') + '?tab=addresses')

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
        return HttpResponseRedirect(reverse('accounts:profile') + '?tab=addresses')

    if request.method == 'POST':
        data = request.POST
        errors = []

        # Validate full_name
        full_name = data.get('full_name', '').strip()
        if not full_name:
            errors.append('Vui lòng nhập họ tên người nhận')
        elif len(full_name) < 4:
            errors.append('Họ tên phải có ít nhất 4 ký tự')
        elif len(full_name.split()) < 2:
            errors.append('Vui lòng nhập đầy đủ họ và tên')

        # Validate phone
        phone = data.get('phone', '').strip().replace(' ', '')
        import re
        phone_pattern = re.compile(r'^(0|\+84)[0-9]{9,10}$')
        if not phone:
            errors.append('Vui lòng nhập số điện thoại')
        elif not phone_pattern.match(phone):
            errors.append('Số điện thoại không hợp lệ (VD: 0912345678)')

        # Validate address
        address_detail = data.get('address', '').strip()
        if not address_detail:
            errors.append('Vui lòng nhập địa chỉ chi tiết')
        elif len(address_detail) < 5:
            errors.append('Địa chỉ phải có ít nhất 5 ký tự')

        # Validate province
        province_code = data.get('province_code', '').strip()
        province_name = data.get('province', '').strip()
        if not province_code or not province_name:
            errors.append('Vui lòng chọn Tỉnh/Thành phố')
        else:
            provinces = AddressService.get_provinces()
            if not any(p['code'] == province_code for p in provinces):
                errors.append('Tỉnh/Thành phố không hợp lệ')

        # Validate district
        district_code = data.get('district_code', '').strip()
        district_name = data.get('district', '').strip()
        if not district_code or not district_name:
            errors.append('Vui lòng chọn Quận/Huyện')
        elif province_code:
            districts = AddressService.get_districts(province_code)
            if not any(d['code'] == district_code for d in districts):
                errors.append('Quận/Huyện không thuộc Tỉnh/Thành phố đã chọn')

        # Validate ward (optional)
        ward_code = data.get('ward_code', '').strip()
        ward_name = data.get('ward', '').strip()
        if ward_code and district_code:
            wards = AddressService.get_wards(district_code)
            if not any(w['code'] == ward_code for w in wards):
                errors.append('Phường/Xã không thuộc Quận/Huyện đã chọn')

        if errors:
            for error in errors:
                messages.error(request, error)
            provinces = AddressService.get_provinces()
            districts = AddressService.get_districts(province_code) if province_code else []
            wards = AddressService.get_wards(district_code) if district_code else []
            address.full_name = full_name
            address.phone = phone
            address.address = address_detail
            address.province = province_name
            address.province_code = province_code
            address.district = district_name
            address.district_code = district_code
            address.ward = ward_name
            address.ward_code = ward_code
            address.is_default = data.get('is_default') == 'on'
            return render(request, 'accounts/address_form.html', {
                'address': address,
                'provinces': provinces,
                'districts': districts,
                'wards': wards,
                'active_tab': 'addresses',
                'is_edit': True
            })

        address.full_name = full_name
        address.phone = phone
        address.address = address_detail
        address.province = province_name
        address.province_code = province_code
        address.district = district_name
        address.district_code = district_code
        address.ward = ward_name
        address.ward_code = ward_code
        address.is_default = data.get('is_default') == 'on'

        address.save()

        messages.success(request, 'Cập nhật địa chỉ thành công!')
        return HttpResponseRedirect(reverse('accounts:profile') + '?tab=addresses')

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

    return HttpResponseRedirect(reverse('accounts:profile') + '?tab=addresses')


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

    return HttpResponseRedirect(reverse('accounts:profile') + '?tab=addresses')


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

        # Parse expiry from MM/YY format
        card_expiry = data.get('card_expiry', '')
        expiry_month = 0
        expiry_year = 0
        if '/' in card_expiry:
            parts = card_expiry.split('/')
            try:
                expiry_month = int(parts[0])
                expiry_year = int(parts[1]) if len(parts[1]) == 2 else int(parts[1][-2:])
            except (ValueError, IndexError):
                pass

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
        return HttpResponseRedirect(reverse('accounts:profile') + '?tab=payments')

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

    return HttpResponseRedirect(reverse('accounts:profile') + '?tab=payments')


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

    return HttpResponseRedirect(reverse('accounts:profile') + '?tab=payments')


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
@rate_limit_class(max_requests=20, window_seconds=60, key_prefix='check_email')
@require_origin_class()
class CheckEmailAPIView(View):
    """
    API endpoint kiểm tra email đã tồn tại chưa

    Security:
    - Rate limited: 20 requests per minute per IP
    - Origin header validation
    - CSRF exempt (required for cross-origin API calls from JS)
    """

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
@rate_limit_class(max_requests=5, window_seconds=60, key_prefix='social_register')
@require_origin_class()
class SocialRegisterAPIView(View):
    """
    API endpoint đăng ký tài khoản qua social

    Security:
    - Rate limited: 5 requests per minute per IP (strict for registration)
    - Origin header validation
    - CSRF exempt (required for cross-origin API calls from JS)
    """

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
@rate_limit_class(max_requests=10, window_seconds=60, key_prefix='social_login')
@require_origin_class()
class SocialLoginAPIView(View):
    """
    API endpoint đăng nhập qua social

    Security:
    - Rate limited: 10 requests per minute per IP
    - Origin header validation
    - CSRF exempt (required for cross-origin API calls from JS)
    """

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


# ============== GOOGLE OAUTH REDIRECT FLOW ==============

def google_login_redirect(request):
    """Redirect to Google OAuth"""
    import urllib.parse

    client_id = settings.GOOGLE_CLIENT_ID

    # Build redirect URI
    redirect_uri = request.build_absolute_uri('/accounts/google/callback/')

    # Google OAuth URL
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        # Force account chooser + consent screen each time
        'prompt': 'consent select_account'
    }

    # Store next URL in session
    next_url = request.GET.get('next', '')
    if next_url:
        request.session['google_auth_next'] = next_url

    google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(google_auth_url)


def google_callback(request):
    """Handle Google OAuth callback"""
    import urllib.parse
    import urllib.request

    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        messages.error(request, f'Đăng nhập Google thất bại: {error}')
        return redirect('accounts:login')

    if not code:
        messages.error(request, 'Không nhận được mã xác thực từ Google')
        return redirect('accounts:login')

    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = request.build_absolute_uri('/accounts/google/callback/')

    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        token_req = urllib.request.Request(
            token_url,
            data=urllib.parse.urlencode(token_data).encode('utf-8'),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(token_req) as response:
            token_response = json.loads(response.read().decode('utf-8'))

        id_token = token_response.get('id_token')
        if not id_token:
            messages.error(request, 'Không nhận được token từ Google')
            return redirect('accounts:login')

        # Decode ID token (JWT) to get user info
        import base64
        payload = id_token.split('.')[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        user_info = json.loads(base64.urlsafe_b64decode(payload).decode('utf-8'))

        email = user_info.get('email', '')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')

        if not email:
            messages.error(request, 'Không lấy được email từ tài khoản Google')
            return redirect('accounts:login')

        # Check if user exists
        email_check = SocialAuthService.check_email_exists(email)

        if email_check['exists']:
            # Login existing user
            result = SocialAuthService.login_social_user(request, email, 'google')
            if result['success']:
                # Create session and login history
                create_user_session(request, result['user'])
                create_login_history(request, result['user'], 'success', 'google')
                messages.success(request, f'Chào mừng {result["user"].first_name}!')
            else:
                messages.error(request, result['error'])
                return redirect('accounts:login')
        else:
            # Register new user
            result = SocialAuthService.create_social_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone='',
                provider='google'
            )
            if result['success']:
                # Login the new user
                login_result = SocialAuthService.login_social_user(request, email, 'google')
                if login_result['success']:
                    # Create session and login history
                    create_user_session(request, login_result['user'])
                    create_login_history(request, login_result['user'], 'success', 'google')
                    messages.success(request, f'Chào mừng {first_name}! Tài khoản đã được tạo.')
            else:
                messages.error(request, result['error'])
                return redirect('accounts:login')

        # Redirect to next URL or home
        next_url = request.session.pop('google_auth_next', None)
        return redirect(next_url if next_url else 'products:home')

    except Exception as e:
        messages.error(request, f'Lỗi khi xác thực với Google: {str(e)}')
        return redirect('accounts:login')


# ============== SECURITY VIEWS ==============

@login_required
@require_POST
def change_password(request):
    """Đổi mật khẩu"""
    form = CustomPasswordChangeForm(request.user, request.POST)

    if form.is_valid():
        user = form.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        # Log password change
        LoginHistory.objects.create(
            user=request.user,
            ip_address=get_client_ip(request),
            device='Password Changed',
            status='success',
            provider='email'
        )

        messages.success(request, 'Đổi mật khẩu thành công!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

    return redirect('accounts:profile')


@login_required
@require_POST
def terminate_session(request, session_id):
    """Kết thúc một phiên đăng nhập"""
    try:
        session = UserSession.objects.get(id=session_id, user=request.user)

        # Don't terminate current session
        if session.session_key == request.session.session_key:
            messages.warning(request, 'Không thể đăng xuất phiên hiện tại.')
            return redirect('accounts:profile')

        # Delete Django session
        from django.contrib.sessions.models import Session
        try:
            Session.objects.filter(session_key=session.session_key).delete()
        except Exception:
            pass

        session.delete()
        messages.success(request, 'Đã đăng xuất thiết bị.')
    except UserSession.DoesNotExist:
        messages.error(request, 'Phiên không tồn tại.')

    return redirect('accounts:profile')


@login_required
@require_POST
def terminate_all_sessions(request):
    """Kết thúc tất cả phiên đăng nhập khác"""
    from django.contrib.sessions.models import Session

    current_session_key = request.session.session_key
    sessions = UserSession.objects.filter(user=request.user).exclude(session_key=current_session_key)

    for session in sessions:
        try:
            Session.objects.filter(session_key=session.session_key).delete()
        except Exception:
            pass

    sessions.delete()
    messages.success(request, 'Đã đăng xuất tất cả thiết bị khác.')

    return redirect('accounts:profile')


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent):
    """Parse user agent string to extract browser, OS, device info"""
    browser = 'Unknown'
    os_name = 'Unknown'
    device = 'Desktop'

    if 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'Edge' in user_agent:
        browser = 'Edge'
    elif 'Opera' in user_agent:
        browser = 'Opera'

    if 'Windows' in user_agent:
        os_name = 'Windows'
    elif 'Mac OS' in user_agent:
        os_name = 'macOS'
    elif 'Linux' in user_agent:
        os_name = 'Linux'
    elif 'Android' in user_agent:
        os_name = 'Android'
        device = 'Mobile'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        os_name = 'iOS'
        device = 'Mobile'

    return {'browser': browser, 'os': os_name, 'device': device}


def create_user_session(request, user):
    """Create a UserSession record for the logged in user"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ua_info = parse_user_agent(user_agent)
    ip = get_client_ip(request)

    # Create new session
    UserSession.objects.create(
        user=user,
        session_key=request.session.session_key or '',
        device=ua_info['device'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        ip_address=ip,
        location='',
        is_current=True
    )


def create_login_history(request, user, status, provider='email'):
    """Create a LoginHistory record"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ua_info = parse_user_agent(user_agent)
    ip = get_client_ip(request)

    LoginHistory.objects.create(
        user=user,
        ip_address=ip,
        device=ua_info['device'],
        browser=ua_info['browser'],
        os=ua_info['os'],
        location='',
        status=status,
        provider=provider,
        user_agent=user_agent
    )

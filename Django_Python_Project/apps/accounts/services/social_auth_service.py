"""
Social Authentication Service
Xử lý đăng nhập/đăng ký qua Google và Facebook
"""
import secrets
import string
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import transaction
from django.db.models import Q

from ..models import Profile, SocialAccount


class SocialAuthService:
    """Service xử lý social login/register"""

    VALID_PROVIDERS = ['google', 'facebook']

    @staticmethod
    def check_email_exists(email: str) -> dict:
        """
        Kiểm tra email đã tồn tại trong hệ thống chưa.
        Kiểm tra cả User.email và User.username (vì email được dùng làm username)
        
        Returns:
            dict: {
                'exists': bool,
                'user_id': int or None,
                'has_social': bool,  # Đã có social account chưa
                'providers': list    # Danh sách providers đã link
            }
        """
        email = email.lower().strip()

        # Tìm user theo email hoặc username (vì email = username)
        user = User.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).first()

        if not user:
            return {
                'exists': False,
                'user_id': None,
                'has_social': False,
                'providers': []
            }

        # Lấy danh sách social providers đã link
        providers = list(
            SocialAccount.objects.filter(user=user).values_list('provider', flat=True)
        )

        return {
            'exists': True,
            'user_id': user.id,
            'has_social': len(providers) > 0,
            'providers': providers
        }

    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """
        Tạo mật khẩu ngẫu nhiên an toàn.
        Đảm bảo có: uppercase, lowercase, digits, special chars
        
        Args:
            length: Độ dài mật khẩu (mặc định 16)
            
        Returns:
            str: Mật khẩu ngẫu nhiên
        """
        if length < 12:
            length = 12

        # Đảm bảo có ít nhất 1 ký tự mỗi loại
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?')
        ]

        # Điền phần còn lại
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))

        # Xáo trộn
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)

    @classmethod
    @transaction.atomic
    def create_social_user(
            cls,
            email: str,
            first_name: str,
            last_name: str,
            phone: str,
            provider: str
    ) -> dict:
        """
        Tạo user mới qua social login.
        Sử dụng email làm username (giống UserRegistrationForm)
        Profile sẽ được tạo tự động qua signal
        
        Args:
            email: Email từ social provider
            first_name: Tên
            last_name: Họ
            phone: Số điện thoại (có thể rỗng)
            provider: 'google' hoặc 'facebook'
            
        Returns:
            dict: {
                'success': bool,
                'user': User or None,
                'error': str or None
            }
        """
        email = email.lower().strip()

        # Validate provider
        if provider not in cls.VALID_PROVIDERS:
            return {
                'success': False,
                'user': None,
                'error': f'Provider không hợp lệ: {provider}'
            }

        # Kiểm tra email đã tồn tại
        if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            return {
                'success': False,
                'user': None,
                'error': 'Email này đã được sử dụng'
            }

        try:
            # Tạo User với email làm username
            password = cls.generate_secure_password()
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name.strip(),
                last_name=last_name.strip()
            )

            # Cập nhật Profile (đã được tạo bởi signal)
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                profile = Profile.objects.create(user=user, email=email)

            profile.email = email
            profile.phone = phone.strip() if phone else ''
            profile.is_social_account = True
            profile.social_provider = provider
            profile.save()

            # Tạo SocialAccount
            SocialAccount.objects.create(
                user=user,
                provider=provider,
                provider_email=email
            )

            return {
                'success': True,
                'user': user,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'user': None,
                'error': str(e)
            }

    @classmethod
    @transaction.atomic
    def link_social_provider(cls, user: User, provider: str, provider_email: str = None) -> dict:
        """
        Liên kết social provider với user hiện có.
        
        Args:
            user: User object
            provider: 'google' hoặc 'facebook'
            provider_email: Email từ provider (mặc định dùng user.email)
            
        Returns:
            dict: {
                'success': bool,
                'error': str or None
            }
        """
        if provider not in cls.VALID_PROVIDERS:
            return {
                'success': False,
                'error': f'Provider không hợp lệ: {provider}'
            }

        provider_email = provider_email or user.email

        # Kiểm tra đã link chưa
        if SocialAccount.objects.filter(user=user, provider=provider).exists():
            return {
                'success': True,
                'error': None  # Đã link rồi, không phải lỗi
            }

        try:
            SocialAccount.objects.create(
                user=user,
                provider=provider,
                provider_email=provider_email.lower().strip()
            )

            # Cập nhật Profile nếu chưa có social info
            if hasattr(user, 'profile'):
                profile = user.profile
                if not profile.is_social_account:
                    profile.is_social_account = True
                    profile.social_provider = provider
                    profile.save()

            return {
                'success': True,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def login_social_user(cls, request, email: str, provider: str) -> dict:
        """
        Đăng nhập user qua social.
        
        Args:
            request: HttpRequest object
            email: Email từ social provider
            provider: 'google' hoặc 'facebook'
            
        Returns:
            dict: {
                'success': bool,
                'user': User or None,
                'error': str or None,
                'redirect_url': str
            }
        """
        email = email.lower().strip()

        if provider not in cls.VALID_PROVIDERS:
            return {
                'success': False,
                'user': None,
                'error': f'Provider không hợp lệ: {provider}',
                'redirect_url': None
            }

        # Tìm user
        user = User.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).first()

        if not user:
            return {
                'success': False,
                'user': None,
                'error': 'Không tìm thấy tài khoản với email này',
                'redirect_url': None
            }

        # Kiểm tra user có active không
        if not user.is_active:
            return {
                'success': False,
                'user': None,
                'error': 'Tài khoản đã bị vô hiệu hóa',
                'redirect_url': None
            }

        # Link provider nếu chưa có
        cls.link_social_provider(user, provider, email)

        # Lưu session key cũ để merge cart
        old_session_key = request.session.session_key

        # Login user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Merge cart (nếu có)
        try:
            from apps.cart.views import merge_session_cart_with_key
            merge_session_cart_with_key(request, old_session_key)
        except ImportError:
            pass  # Cart app không có hoặc function không tồn tại

        # Xác định redirect URL
        redirect_url = request.GET.get('next', 'products:home')

        return {
            'success': True,
            'user': user,
            'error': None,
            'redirect_url': redirect_url
        }

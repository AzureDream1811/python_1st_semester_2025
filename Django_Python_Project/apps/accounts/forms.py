from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile, Address

class UserRegistrationForm(UserCreationForm):
    """
    Form đăng ký tài khoản: Tạo User và Profile cùng lúc
    Tự động đồng bộ email từ User sang Profile
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[Profile.phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại (không bắt buộc)'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']  # Password được xử lý bởi UserCreationForm

    def __init__(self, *args, **kwargs):
        """
        Tùy chỉnh widget cho password1 và password2
        """
        super().__init__(*args, **kwargs)

        # Tùy chỉnh widget cho password1 (Nhập mật khẩu)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
        self.fields['password1'].label = 'Mật khẩu'
        self.fields['password1'].help_text = 'Mật khẩu phải có ít nhất 8 ký tự'

        # Tùy chỉnh widget cho password2 (Xác nhận mật khẩu)
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
        self.fields['password2'].label = 'Xác nhận mật khẩu'
        self.fields['password2'].help_text = 'Nhập lại mật khẩu để xác nhận'

    def clean_email(self):
        """
        Validate email không được trùng trong hệ thống
        Email sẽ được dùng làm username
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email.lower().strip()

    def save(self, commit=True):
        """
        Override save để:
        1. Tạo User với email làm username
        2. Tạo Profile và lưu số điện thoại
        """
        # 1. Lưu User trước
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Dùng email làm username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

            # 2. Tạo Profile và lưu số điện thoại
            # Kiểm tra xem profile đã được tạo bởi signal chưa
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                profile = Profile(user=user)

            profile.phone = self.cleaned_data.get('phone')
            profile.email = user.email  # Đồng bộ email sang profile
            profile.save()

        return user

class UserLoginForm(AuthenticationForm):
    """
    Form đăng nhập
    Chấp nhận cả email và username
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập hoặc Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    # Remember me để duy trì session lâu hơn
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Ghi nhớ đăng nhập"
    )


class UserUpdateForm(forms.ModelForm):
    """
    Form cập nhật thông tin cơ bản của User
    Email thường không cho đổi để tránh conflict với username
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'  # Không cho đổi email
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form cập nhật thông tin Profile
    Bao gồm: Avatar, SĐT, Địa chỉ, Ngày sinh, Giới tính
    """
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth', 'gender', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Địa chỉ của bạn'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Form đổi mật khẩu với style Bootstrap
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tùy chỉnh widget và label cho từng field
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu hiện tại'
        })
        self.fields['old_password'].label = 'Mật khẩu hiện tại'

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu mới'
        })
        self.fields['new_password1'].label = 'Mật khẩu mới'
        self.fields['new_password1'].help_text = 'Mật khẩu phải có ít nhất 8 ký tự'

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu mới'
        })
        self.fields['new_password2'].label = 'Xác nhận mật khẩu mới'
        self.fields['new_password2'].help_text = 'Nhập lại mật khẩu mới để xác nhận'


class AddressForm(forms.ModelForm):
    """
    Form địa chỉ giao hàng
    Tích hợp API provinces.open-api.vn để chọn Tỉnh/Thành phố, Quận/Huyện, Phường/Xã
    JavaScript sẽ xử lý việc load data từ API
    """

    class Meta:
        model = Address
        fields = [
            'full_name',
            'address',
            'city', 'city_code',
            'district', 'district_code',
            'ward', 'ward_code'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ tên người nhận'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Địa chỉ cụ thể (Số nhà, tên đường...)'
            }),

            # Select cho city, district, ward với API URL
            'city': forms.Select(attrs={
                'class': 'form-select',
                'id': 'city-select',
                'required': True,
                'data-api-url': 'https://provinces.open-api.vn/api/p/'
            }),
            'district': forms.Select(attrs={
                'class': 'form-select',
                'id': 'district-select',
                'required': True,
                'disabled': True  # Disable cho đến khi chọn city
            }),
            'ward': forms.Select(attrs={
                'class': 'form-select',
                'id': 'ward-select',
                'required': False,
                'disabled': True  # Disable cho đến khi chọn district
            }),

            # Hidden inputs cho các code (JS sẽ điền vào)
            'city_code': forms.HiddenInput(),
            'district_code': forms.HiddenInput(),
            'ward_code': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Khởi tạo form và thêm option mặc định cho các select
        """
        super().__init__(*args, **kwargs)

        # Thêm option mặc định cho các dropdown (JS sẽ populate các options khác)
        self.fields['city'].widget.choices = [('', '-- Chọn Tỉnh/Thành phố --')]
        self.fields['district'].widget.choices = [('', '-- Chọn Quận/Huyện --')]
        self.fields['ward'].widget.choices = [('', '-- Chọn Phường/Xã (không bắt buộc) --')]

        # Ward không bắt buộc
        self.fields['ward'].required = False

    def clean_full_name(self):
        """Validate họ tên người nhận"""
        full_name = self.cleaned_data.get('full_name')

        if not full_name or len(full_name.strip()) < 2:
            raise forms.ValidationError('Vui lòng nhập họ tên người nhận')

        # Kiểm tra có ít nhất 2 từ
        words = full_name.strip().split()
        if len(words) < 2:
            raise forms.ValidationError('Vui lòng nhập đầy đủ họ và tên (ít nhất 2 từ)')

        return full_name.strip().title()

    def clean_address(self):
        """Validate địa chỉ chi tiết"""
        address = self.cleaned_data.get('address')

        if not address or len(address.strip()) < 5:
            raise forms.ValidationError('Vui lòng nhập địa chỉ chi tiết (số nhà, tên đường)')

        return address.strip()

    def clean_city(self):
        """Validate tỉnh/thành phố"""
        city = self.cleaned_data.get('city')

        if not city:
            raise forms.ValidationError('Vui lòng chọn Tỉnh/Thành phố')

        return city.strip()

    def clean_district(self):
        """Validate quận/huyện"""
        district = self.cleaned_data.get('district')

        if not district:
            raise forms.ValidationError('Vui lòng chọn Quận/Huyện')

        return district.strip()

    def clean(self):
        """
        Validate toàn bộ form
        Kiểm tra các điều kiện phụ thuộc
        """
        cleaned_data = super().clean()

        city = cleaned_data.get('city')
        district = cleaned_data.get('district')

        # Đảm bảo nếu chọn district thì phải có city
        if district and not city:
            raise forms.ValidationError('Vui lòng chọn Tỉnh/Thành phố trước khi chọn Quận/Huyện')

        return cleaned_data
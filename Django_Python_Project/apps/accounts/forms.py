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
                'placeholder': 'Tên',
                'minlength': '2',
                'maxlength': '50'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ',
                'minlength': '2',
                'maxlength': '50'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.is_social_account = kwargs.pop('is_social_account', False)
        super().__init__(*args, **kwargs)

        if self.is_social_account:
            self.fields['email'].widget.attrs['readonly'] = 'readonly'
            self.fields['email'].help_text = 'Email không thể thay đổi với tài khoản Google'

    def clean_first_name(self):
        import re
        first_name = self.cleaned_data.get('first_name', '').strip()

        if not first_name:
            raise forms.ValidationError('Vui lòng nhập tên.')
        if len(first_name) < 2:
            raise forms.ValidationError('Tên phải có ít nhất 2 ký tự.')
        if len(first_name) > 50:
            raise forms.ValidationError('Tên không được quá 50 ký tự.')

        vietnamese_pattern = r'^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s]+$'
        if not re.match(vietnamese_pattern, first_name):
            raise forms.ValidationError('Tên chỉ được chứa chữ cái và khoảng trắng.')

        return first_name.strip()

    def clean_last_name(self):
        import re
        last_name = self.cleaned_data.get('last_name', '').strip()

        if not last_name:
            raise forms.ValidationError('Vui lòng nhập họ.')
        if len(last_name) < 2:
            raise forms.ValidationError('Họ phải có ít nhất 2 ký tự.')
        if len(last_name) > 50:
            raise forms.ValidationError('Họ không được quá 50 ký tự.')

        vietnamese_pattern = r'^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s]+$'
        if not re.match(vietnamese_pattern, last_name):
            raise forms.ValidationError('Họ chỉ được chứa chữ cái và khoảng trắng.')

        return last_name.strip()


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
                'placeholder': 'Số điện thoại (VD: 0912345678)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Địa chỉ của bạn',
                'minlength': '10',
                'maxlength': '500'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            }),
        }

    def clean_phone(self):
        import re
        phone = self.cleaned_data.get('phone', '').strip()

        if not phone:
            return ''

        pattern = r'^(0|\+84)[0-9]{9,10}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError('Số điện thoại không hợp lệ. VD: 0912345678 hoặc +84912345678')

        existing = Profile.objects.filter(phone=phone).exclude(pk=self.instance.pk if self.instance else None)
        if existing.exists():
            raise forms.ValidationError('Số điện thoại này đã được sử dụng.')

        return phone

    def clean_date_of_birth(self):
        from datetime import date
        dob = self.cleaned_data.get('date_of_birth')

        if not dob:
            return None

        today = date.today()

        if dob > today:
            raise forms.ValidationError('Ngày sinh không thể là ngày trong tương lai.')

        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 13:
            raise forms.ValidationError('Bạn phải từ 13 tuổi trở lên.')
        if age > 120:
            raise forms.ValidationError('Ngày sinh không hợp lệ.')

        return dob

    def clean_gender(self):
        gender = self.cleaned_data.get('gender', '')
        valid_genders = ['', 'male', 'female', 'other']

        if gender and gender not in valid_genders:
            raise forms.ValidationError('Giới tính không hợp lệ.')

        return gender

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        if hasattr(avatar, 'size') and avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Ảnh đại diện không được vượt quá 5MB.')

        if hasattr(avatar, 'content_type'):
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if avatar.content_type not in allowed_types:
                raise forms.ValidationError('Chỉ chấp nhận định dạng JPG, PNG hoặc WebP.')

        return avatar

    def clean_address(self):
        address = self.cleaned_data.get('address', '').strip()

        if not address:
            return ''

        if len(address) < 10:
            raise forms.ValidationError('Địa chỉ phải có ít nhất 10 ký tự.')
        if len(address) > 500:
            raise forms.ValidationError('Địa chỉ không được quá 500 ký tự.')

        return address


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Form đổi mật khẩu với style Bootstrap và validation nâng cao
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu hiện tại'
        })
        self.fields['old_password'].label = 'Mật khẩu hiện tại'

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu mới',
            'id': 'new_password1'
        })
        self.fields['new_password1'].label = 'Mật khẩu mới'
        self.fields['new_password1'].help_text = ''

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu mới'
        })
        self.fields['new_password2'].label = 'Xác nhận mật khẩu mới'
        self.fields['new_password2'].help_text = ''

    def clean_new_password1(self):
        import re
        password = self.cleaned_data.get('new_password1')
        old_password = self.cleaned_data.get('old_password')

        if not password:
            raise forms.ValidationError('Vui lòng nhập mật khẩu mới.')

        if len(password) < 8:
            raise forms.ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Mật khẩu phải có ít nhất 1 chữ hoa.')

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Mật khẩu phải có ít nhất 1 chữ thường.')

        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Mật khẩu phải có ít nhất 1 số.')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Mật khẩu phải có ít nhất 1 ký tự đặc biệt.')

        if old_password and password == old_password:
            raise forms.ValidationError('Mật khẩu mới không được giống mật khẩu cũ.')

        user = self.user
        if user:
            user_info = [
                user.email.split('@')[0] if user.email else '',
                user.first_name.lower() if user.first_name else '',
                user.last_name.lower() if user.last_name else ''
            ]
            password_lower = password.lower()
            for info in user_info:
                if info and len(info) >= 3 and info in password_lower:
                    raise forms.ValidationError('Mật khẩu không được chứa tên hoặc email của bạn.')

        return password


class AddressForm(forms.ModelForm):
    """
    Form địa chỉ giao hàng
    
    Tích hợp API provinces.open-api.vn để chọn Tỉnh/Thành phố, Quận/Huyện, Phường/Xã
    JavaScript sẽ xử lý việc load data từ API
    
    LƯU Ý: Model Address sử dụng 'province' thay vì 'city'
    """

    class Meta:
        model = Address
        # SỬA LỖI: Đổi 'city' thành 'province' theo model Address
        fields = [
            'full_name',
            'phone',
            'address',
            'province', 'province_code',
            'district', 'district_code',
            'ward', 'ward_code'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ tên người nhận'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Địa chỉ cụ thể (Số nhà, tên đường...)'
            }),

            # Select cho province, district, ward với API URL
            # SỬA LỖI: Đổi 'city' thành 'province'
            'province': forms.Select(attrs={
                'class': 'form-select',
                'id': 'province-select',
                'required': True,
                'data-api-url': 'https://provinces.open-api.vn/api/p/'
            }),
            'district': forms.Select(attrs={
                'class': 'form-select',
                'id': 'district-select',
                'required': True,
                'disabled': True  # Disable cho đến khi chọn province
            }),
            'ward': forms.Select(attrs={
                'class': 'form-select',
                'id': 'ward-select',
                'required': False,
                'disabled': True  # Disable cho đến khi chọn district
            }),

            # Hidden inputs cho các code (JS sẽ điền vào)
            'province_code': forms.HiddenInput(),
            'district_code': forms.HiddenInput(),
            'ward_code': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Khởi tạo form và thêm option mặc định cho các select
        """
        super().__init__(*args, **kwargs)

        # Thêm option mặc định cho các dropdown (JS sẽ populate các options khác)
        self.fields['province'].widget.choices = [('', '-- Chọn Tỉnh/Thành phố --')]
        self.fields['district'].widget.choices = [('', '-- Chọn Quận/Huyện --')]
        self.fields['ward'].widget.choices = [('', '-- Chọn Phường/Xã (không bắt buộc) --')]

        # Ward không bắt buộc
        self.fields['ward'].required = False
        self.fields['ward_code'].required = False

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

    def clean_province(self):
        """Validate tỉnh/thành phố"""
        province = self.cleaned_data.get('province')

        if not province:
            raise forms.ValidationError('Vui lòng chọn Tỉnh/Thành phố')

        return province.strip()

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

        province = cleaned_data.get('province')
        district = cleaned_data.get('district')

        # Đảm bảo nếu chọn district thì phải có province
        if district and not province:
            raise forms.ValidationError('Vui lòng chọn Tỉnh/Thành phố trước khi chọn Quận/Huyện')

        return cleaned_data

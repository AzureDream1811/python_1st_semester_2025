from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Order


class CheckoutForm(forms.ModelForm):
    """
    Form thanh toán cho đơn hàng
    Tích hợp API provinces.open-api.vn để chọn Tỉnh/Thành phố, Quận/Huyện, Phường/Xã
    """

    # Validator cho số điện thoại Việt Nam
    phone_regex = RegexValidator(
        regex=r'^(0|\+84)[0-9]{9,10}$',
        message="Số điện thoại phải có định dạng: '0xxxxxxxxx' hoặc '+84xxxxxxxxx'"
    )

    # Thêm các trường ẩn để lưu code từ API
    city_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_city_code'})
    )
    district_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_district_code'})
    )
    ward_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_ward_code'})
    )

    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone',
            'city', 'district', 'ward', 'address',
            'note', 'payment_method'
        ]

        # Tùy chỉnh giao diện các trường input với Bootstrap
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Họ và tên người nhận',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại (VD: 0912345678)',
                'required': True
            }),

            # Đổi city, district, ward thành Select để tích hợp API
            'city': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_city',
                'required': True,
                'data-api-url': 'https://provinces.open-api.vn/api/p/'  # API URL để load provinces
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_district',
                'required': True,
                'disabled': True  # Disable cho đến khi chọn city
            }),
            'ward': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_ward',
                'required': False,
                'disabled': True  # Disable cho đến khi chọn district
            }),

            # Address đặt sau city, district, ward
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa chỉ chi tiết (số nhà, tên đường)',
                'required': True
            }),

            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ghi chú thêm cho đơn hàng (không bắt buộc)',
                'rows': 3,
                'required': False
            }),

            # RadioSelect để hiển thị các phương thức thanh toán
            'payment_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Khởi tạo form và tự động điền thông tin từ User, Profile, Address
        Xử lý initial choices cho city, district, ward
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Thêm validator cho trường phone
        self.fields['phone'].validators.append(self.phone_regex)

        # Thêm option mặc định cho các dropdown
        self.fields['city'].choices = [('', 'Chọn Tỉnh/Thành phố')]
        self.fields['district'].choices = [('', 'Chọn Quận/Huyện')]
        self.fields['ward'].choices = [('', 'Chọn Phường/Xã (không bắt buộc)')]

        # Pre-fill thông tin nếu user đã đăng nhập
        if user and user.is_authenticated:
            # 1. Điền họ tên từ User model
            full_name = user.get_full_name().strip()
            if full_name:
                self.fields['full_name'].initial = full_name
            else:
                self.fields['full_name'].initial = user.username

            # 2. Điền email từ User model
            if user.email:
                self.fields['email'].initial = user.email

            # 3. Điền số điện thoại từ Profile model
            try:
                if hasattr(user, 'profile') and user.profile.phone:
                    self.fields['phone'].initial = user.profile.phone
            except Exception:
                pass

            # 4. Điền địa chỉ từ Address model (địa chỉ mặc định hoặc mới nhất)
            try:
                default_address = user.addresses.filter(is_default=True).first()
                if not default_address:
                    default_address = user.addresses.order_by('-created_at').first()

                if default_address:
                    self.fields['full_name'].initial = default_address.full_name
                    self.fields['address'].initial = default_address.address

                    # Điền city, district, ward và các code
                    # JavaScript sẽ xử lý việc load lại dropdown dựa vào các giá trị này
                    if default_address.city:
                        self.fields['city'].initial = default_address.city
                        if default_address.city_code:
                            self.fields['city_code'].initial = default_address.city_code

                    if default_address.district:
                        self.fields['district'].initial = default_address.district
                        if default_address.district_code:
                            self.fields['district_code'].initial = default_address.district_code

                    if default_address.ward:
                        self.fields['ward'].initial = default_address.ward
                        if default_address.ward_code:
                            self.fields['ward_code'].initial = default_address.ward_code
            except Exception:
                pass

    def clean_phone(self):
        """Validate số điện thoại Việt Nam"""
        phone = self.cleaned_data.get('phone')

        if not phone:
            raise ValidationError('Vui lòng nhập số điện thoại')

        # Loại bỏ khoảng trắng, dấu gạch ngang, dấu chấm
        phone = phone.replace(' ', '').replace('-', '').replace('.', '')

        # Kiểm tra độ dài
        if len(phone) < 10:
            raise ValidationError('Số điện thoại phải có ít nhất 10 chữ số')

        if len(phone) > 12:
            raise ValidationError('Số điện thoại không hợp lệ')

        return phone

    def clean_full_name(self):
        """Validate họ tên người nhận"""
        full_name = self.cleaned_data.get('full_name')

        if not full_name or len(full_name.strip()) < 2:
            raise ValidationError('Vui lòng nhập họ và tên người nhận')

        # Kiểm tra có ít nhất 2 từ
        words = full_name.strip().split()
        if len(words) < 2:
            raise ValidationError('Vui lòng nhập đầy đủ họ và tên (ít nhất 2 từ)')

        # Kiểm tra không chứa số
        if any(char.isdigit() for char in full_name):
            raise ValidationError('Họ tên không được chứa số')

        return full_name.strip().title()

    def clean_address(self):
        """Validate địa chỉ chi tiết"""
        address = self.cleaned_data.get('address')

        if not address or len(address.strip()) < 5:
            raise ValidationError('Vui lòng nhập địa chỉ chi tiết (số nhà, tên đường)')

        return address.strip()

    def clean_city(self):
        """Validate tỉnh/thành phố"""
        city = self.cleaned_data.get('city')

        if not city:
            raise ValidationError('Vui lòng chọn Tỉnh/Thành phố')

        return city.strip()

    def clean_district(self):
        """Validate quận/huyện"""
        district = self.cleaned_data.get('district')

        if not district:
            raise ValidationError('Vui lòng chọn Quận/Huyện')

        return district.strip()

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError('Vui lòng nhập email')

        return email.lower().strip()

    def clean(self):
        """Validate toàn bộ form"""
        cleaned_data = super().clean()

        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')

        # Đảm bảo có đủ thông tin liên hệ
        if not phone and not email:
            raise ValidationError(
                'Vui lòng cung cấp ít nhất một thông tin liên hệ (email hoặc số điện thoại)'
            )

        # Kiểm tra số điện thoại không chứa chữ cái
        if phone and any(char.isalpha() for char in phone):
            self.add_error('phone', 'Số điện thoại không được chứa chữ cái')

        return cleaned_data

    def save(self, commit=True):
        """
        Override save để lưu cả city_code, district_code, ward_code vào model
        (nếu bạn có các trường này trong Order model)
        """
        instance = super().save(commit=False)

        # Lưu các code từ hidden fields (nếu Order model có các trường này)
        if hasattr(instance, 'city_code'):
            instance.city_code = self.cleaned_data.get('city_code', '')
        if hasattr(instance, 'district_code'):
            instance.district_code = self.cleaned_data.get('district_code', '')
        if hasattr(instance, 'ward_code'):
            instance.ward_code = self.cleaned_data.get('ward_code', '')

        if commit:
            instance.save()

        return instance

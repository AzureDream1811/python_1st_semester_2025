from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Form đăng ký tài khoản"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email của bạn'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Dùng email làm username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Form đăng nhập"""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserUpdateForm(forms.ModelForm):
    """Form cập nhật thông tin người dùng"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address', 'date_of_birth', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form đổi mật khẩu"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu hiện tại'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mật khẩu mới'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu mới'
        })
    )


class AddressForm(forms.ModelForm):
    """Form địa chỉ giao hàng"""
    
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'ward', 'district', 'city', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên người nhận'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ chi tiết'}),
            'ward': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phường/Xã'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quận/Huyện'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tỉnh/Thành phố'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

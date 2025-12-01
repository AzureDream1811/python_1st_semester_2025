from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone', 'is_verified', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('phone', 'address', 'avatar', 'date_of_birth', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'city', 'district', 'user', 'is_default']
    list_filter = ['city', 'is_default']
    search_fields = ['full_name', 'phone', 'address_line']
    raw_id_fields = ['user']

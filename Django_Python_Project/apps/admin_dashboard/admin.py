"""
Admin registrations cho ElectroShop Admin Dashboard
Import và đăng ký tất cả models vào custom admin site
"""
from django.contrib import admin

# Cấu hình admin site mặc định
admin.site.site_header = "🔌 ElectroShop Admin"
admin.site.site_title = "ElectroShop"
admin.site.index_title = "Quản trị hệ thống bán hàng điện gia dụng"

"""
Admin Configuration cho Search App - ElectroShop

Search app không có models riêng.
Sử dụng:
- Product, Category, Brand từ products app
- SearchLog từ analytics app

Để xem lịch sử tìm kiếm, vào Analytics > SearchLog trong admin.
"""
from django.contrib import admin

# Search app không có Django models để đăng ký
# Dữ liệu tìm kiếm được lưu trong SearchLog (analytics app)

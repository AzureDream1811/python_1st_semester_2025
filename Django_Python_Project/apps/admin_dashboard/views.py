from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView

# Local Imports
from .decorators import StaffRequiredMixin
from .forms import (
    ProductForm, CategoryForm, BrandForm, OrderStatusForm,
    UserEditForm, VoucherForm, FlashSaleForm
)
from .services.statistics import DashboardStatistics
from apps.orders.models import Order, OrderHistory
from apps.products.models import Product, Category, Brand
from apps.promotions.models import Voucher, FlashSale
from apps.reviews.models import Review


# ==========================================
# 1. DASHBOARD & ANALYTICS
# ==========================================

class DashboardView(StaffRequiredMixin, TemplateView):
    """Trang dashboard chính"""
    template_name = 'admin_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = DashboardStatistics()
        context['stats'] = stats.get_dashboard_summary()
        context['recent_orders'] = Order.objects.select_related('user').order_by('-created_at')[:10]
        return context


class ChartDataView(StaffRequiredMixin, View):
    """API endpoint cung cấp dữ liệu cho biểu đồ"""

    def get(self, request):
        chart_type = request.GET.get('type', 'revenue')
        stats = DashboardStatistics()

        if chart_type == 'revenue':
            return JsonResponse(stats.get_daily_revenue_chart_data())
        elif chart_type == 'orders':
            return JsonResponse(stats.get_order_status_chart_data())
        elif chart_type == 'sentiment':
            return JsonResponse(stats.get_sentiment_chart_data())
        elif chart_type == 'category':
            return JsonResponse(stats.get_category_revenue_chart_data())

        return JsonResponse({'error': 'Invalid chart type'}, status=400)


class RevenueReportPageView(StaffRequiredMixin, TemplateView):
    """Trang báo cáo doanh thu"""
    template_name = 'admin/revenue_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now().date()
        context['end_date'] = today.isoformat()
        context['start_date'] = (today - timedelta(days=30)).isoformat()
        return context


class RevenueReportView(StaffRequiredMixin, View):
    """API endpoint cho báo cáo doanh thu"""

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        stats = DashboardStatistics()

        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = datetime.now().date()
            start = end - timedelta(days=30)

        report = stats.get_revenue_report(start, end)
        return JsonResponse(report)


# ==========================================
# 2. ORDER MANAGEMENT
# ==========================================

class OrderListView(StaffRequiredMixin, ListView):
    """Danh sách đơn hàng"""
    model = Order
    template_name = 'admin_dashboard/orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related('user').order_by('-created_at')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) | Q(full_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.STATUS_CHOICES
        return context


class OrderDetailView(StaffRequiredMixin, DetailView):
    """Chi tiết đơn hàng"""
    model = Order
    template_name = 'admin_dashboard/orders/detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = OrderStatusForm(initial={'status': self.object.status})
        context['history'] = self.object.history.all()
        return context


class OrderStatusUpdateView(StaffRequiredMixin, View):
    """Cập nhật trạng thái đơn hàng"""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            old_status = order.status
            new_status = form.cleaned_data['status']
            order.status = new_status
            order.save()

            # Tạo lịch sử
            OrderHistory.objects.create(
                order=order,
                status=new_status
            )
            messages.success(request, f'Cập nhật trạng thái từ {old_status} sang {new_status}')
        return redirect('admin_dashboard:order_detail', pk=pk)


# ==========================================
# 3. CATALOG MANAGEMENT (Products, Categories, Brands)
# ==========================================

# --- Products ---

class ProductListView(StaffRequiredMixin, ListView):
    """Danh sách sản phẩm"""
    model = Product
    template_name = 'admin_dashboard/products/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'brand').order_by('-created_at')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        return queryset


class ProductCreateView(StaffRequiredMixin, CreateView):
    """Tạo sản phẩm mới"""
    model = Product
    form_class = ProductForm
    template_name = 'admin_dashboard/products/form.html'
    success_url = reverse_lazy('admin_dashboard:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo sản phẩm thành công!')
        return super().form_valid(form)


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    """Cập nhật sản phẩm"""
    model = Product
    form_class = ProductForm
    template_name = 'admin_dashboard/products/form.html'
    success_url = reverse_lazy('admin_dashboard:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật sản phẩm thành công!')
        return super().form_valid(form)


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    """Xóa sản phẩm"""
    model = Product
    success_url = reverse_lazy('admin_dashboard:product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Xóa sản phẩm thành công!')
        return super().delete(request, *args, **kwargs)


# --- Categories ---

class CategoryListView(StaffRequiredMixin, ListView):
    """Danh sách danh mục"""
    model = Category
    template_name = 'admin_dashboard/categories/list.html'
    context_object_name = 'categories'
    paginate_by = 20


class CategoryCreateView(StaffRequiredMixin, CreateView):
    """Tạo danh mục mới"""
    model = Category
    form_class = CategoryForm
    template_name = 'admin_dashboard/categories/form.html'
    success_url = reverse_lazy('admin_dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo danh mục thành công!')
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Cập nhật danh mục"""
    model = Category
    form_class = CategoryForm
    template_name = 'admin_dashboard/categories/form.html'
    success_url = reverse_lazy('admin_dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật danh mục thành công!')
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Xóa danh mục"""
    model = Category
    success_url = reverse_lazy('admin_dashboard:category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Xóa danh mục thành công!')
        return super().delete(request, *args, **kwargs)


# --- Brands ---

class BrandListView(StaffRequiredMixin, ListView):
    """Danh sách thương hiệu"""
    model = Brand
    template_name = 'admin_dashboard/brands/list.html'
    context_object_name = 'brands'
    paginate_by = 20


class BrandCreateView(StaffRequiredMixin, CreateView):
    """Tạo thương hiệu mới"""
    model = Brand
    form_class = BrandForm
    template_name = 'admin_dashboard/brands/form.html'
    success_url = reverse_lazy('admin_dashboard:brand_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo thương hiệu thành công!')
        return super().form_valid(form)


class BrandUpdateView(StaffRequiredMixin, UpdateView):
    """Cập nhật thương hiệu"""
    model = Brand
    form_class = BrandForm
    template_name = 'admin_dashboard/brands/form.html'
    success_url = reverse_lazy('admin_dashboard:brand_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật thương hiệu thành công!')
        return super().form_valid(form)


class BrandDeleteView(StaffRequiredMixin, DeleteView):
    """Xóa thương hiệu"""
    model = Brand
    success_url = reverse_lazy('admin_dashboard:brand_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Xóa thương hiệu thành công!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# 4. USER MANAGEMENT
# ==========================================

class UserListView(StaffRequiredMixin, ListView):
    """Danh sách người dùng"""
    model = User
    template_name = 'admin_dashboard/users/list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.order_by('-date_joined')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset


class UserDetailView(StaffRequiredMixin, DetailView):
    """Chi tiết người dùng"""
    model = User
    template_name = 'admin_dashboard/users/detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.object).order_by('-created_at')[:10]
        context['edit_form'] = UserEditForm(instance=self.object)
        return context


class UserUpdateView(StaffRequiredMixin, UpdateView):
    """Cập nhật quyền người dùng"""
    model = User
    form_class = UserEditForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Cập nhật quyền người dùng thành công!')
        return redirect('admin_dashboard:user_detail', pk=self.object.pk)


# ==========================================
# 5. REVIEW MANAGEMENT
# ==========================================

class ReviewListView(StaffRequiredMixin, ListView):
    """Danh sách đánh giá"""
    model = Review
    template_name = 'admin_dashboard/reviews/list.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        queryset = Review.objects.select_related('product', 'user').order_by('-created_at')
        sentiment = self.request.GET.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)
        return queryset


class ReviewApproveView(StaffRequiredMixin, View):
    """Duyệt đánh giá"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = True
        review.save()
        messages.success(request, 'Đã duyệt đánh giá!')
        return redirect('admin_dashboard:review_list')


class ReviewRejectView(StaffRequiredMixin, View):
    """Từ chối đánh giá"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = False
        review.save()
        messages.success(request, 'Đã từ chối đánh giá!')
        return redirect('admin_dashboard:review_list')


# ==========================================
# 6. PROMOTION MANAGEMENT (Vouchers, Flash Sales)
# ==========================================

class VoucherListView(StaffRequiredMixin, ListView):
    """Danh sách voucher"""
    model = Voucher
    template_name = 'admin_dashboard/promotions/vouchers.html'
    context_object_name = 'vouchers'
    paginate_by = 20


class VoucherCreateView(StaffRequiredMixin, CreateView):
    """Tạo voucher mới"""
    model = Voucher
    form_class = VoucherForm
    template_name = 'admin_dashboard/promotions/voucher_form.html'
    success_url = reverse_lazy('admin_dashboard:voucher_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo voucher thành công!')
        return super().form_valid(form)


class FlashSaleListView(StaffRequiredMixin, ListView):
    """Danh sách flash sale"""
    model = FlashSale
    template_name = 'admin_dashboard/promotions/flash_sales.html'
    context_object_name = 'flash_sales'
    paginate_by = 20


class FlashSaleCreateView(StaffRequiredMixin, CreateView):
    """Tạo flash sale mới"""
    model = FlashSale
    form_class = FlashSaleForm
    template_name = 'admin_dashboard/promotions/flash_sale_form.html'
    success_url = reverse_lazy('admin_dashboard:flash_sale_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo flash sale thành công!')
        return super().form_valid(form)

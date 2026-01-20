"""
Views cho Admin Dashboard
"""
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .decorators import StaffRequiredMixin
from .services.statistics import DashboardStatistics
from .forms import (
    ProductForm, CategoryForm, BrandForm, OrderStatusForm,
    UserEditForm, VoucherForm, FlashSaleForm, NotificationForm
)
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order, OrderHistory
from apps.reviews.models import Review
from apps.promotions.models import Voucher, FlashSale
from apps.notifications.models import Notification


# ==================== Dashboard ====================

class DashboardView(StaffRequiredMixin, TemplateView):
    """Trang dashboard chính"""
    template_name = 'admin_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        period = self.request.GET.get('period', 'month')
        custom_start = None
        custom_end = None

        if period == 'custom':
            start_str = self.request.GET.get('start_date')
            end_str = self.request.GET.get('end_date')
            if start_str and end_str:
                try:
                    custom_start = datetime.strptime(start_str, '%Y-%m-%d').date()
                    custom_end = datetime.strptime(end_str, '%Y-%m-%d').date()
                    if custom_start > custom_end:
                        custom_start, custom_end = custom_end, custom_start
                except ValueError:
                    period = 'month'
            else:
                period = 'month'

        stats = DashboardStatistics()
        context['stats'] = stats.get_dashboard_summary(period, custom_start, custom_end)
        context['current_period'] = period
        context['recent_orders'] = Order.objects.select_related('user').order_by('-created_at')[:10]
        return context


# ==================== Product Management ====================

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


# ==================== Order Management ====================

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
        # Lấy danh sách trạng thái hợp lệ có thể chuyển đến
        allowed_transitions = self.object.get_allowed_transitions()
        context['allowed_transitions'] = allowed_transitions
        context['history'] = self.object.history.all()
        return context


class OrderStatusUpdateView(StaffRequiredMixin, View):
    """Cập nhật trạng thái đơn hàng"""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            note = form.cleaned_data.get('note', '')

            # Sử dụng method transition_to với validation
            success, message = order.transition_to(new_status, note=note)

            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        else:
            messages.error(request, 'Dữ liệu không hợp lệ')
        return redirect('admin_dashboard:order_detail', pk=pk)


# ==================== User Management ====================

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


# ==================== Category Management ====================

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


# ==================== Brand Management ====================

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


# ==================== Review Management ====================

class ReviewListView(StaffRequiredMixin, ListView):
    """Danh sách đánh giá"""
    model = Review
    template_name = 'admin_dashboard/reviews/list.html'
    context_object_name = 'reviews'
    paginate_by = 20

    def get_queryset(self):
        queryset = Review.objects.select_related('product', 'product__category', 'product__brand', 'user').order_by('-created_at')

        # Filter by sentiment
        sentiment = self.request.GET.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)

        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=int(rating))

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'approved':
            queryset = queryset.filter(is_approved=True)
        elif status == 'pending':
            queryset = queryset.filter(is_approved=False)

        # Filter by AI mismatch
        ai_check = self.request.GET.get('ai_check')
        if ai_check == 'mismatch':
            from django.db.models import Q
            queryset = queryset.filter(
                Q(rating__gte=4, sentiment='negative') |
                Q(rating__lte=2, sentiment='positive')
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Q

        # Thống kê
        context['total_count'] = Review.objects.count()
        context['positive_count'] = Review.objects.filter(sentiment='positive').count()
        context['neutral_count'] = Review.objects.filter(sentiment='neutral').count()
        context['negative_count'] = Review.objects.filter(sentiment='negative').count()
        context['mismatch_count'] = Review.objects.filter(
            Q(rating__gte=4, sentiment='negative') |
            Q(rating__lte=2, sentiment='positive')
        ).count()

        return context


class ReviewDetailAPIView(StaffRequiredMixin, View):
    """API trả về chi tiết review cho modal"""

    def get(self, request, pk):
        review = get_object_or_404(Review, pk=pk)

        # Lấy thông tin mismatch
        mismatch_info = review.rating_sentiment_mismatch

        # Xử lý image URL (có thể là URL ngoại hoặc local file)
        product_image = None
        if review.product.image:
            image_name = str(review.product.image.name) if hasattr(review.product.image, 'name') else str(review.product.image)
            if image_name.startswith(('http://', 'https://')):
                product_image = image_name
            else:
                try:
                    product_image = review.product.image.url
                except (ValueError, AttributeError):
                    pass

        data = {
            'success': True,
            'review': {
                'id': review.pk,
                'username': review.user.username,
                'user_email': review.user.email,
                'product_name': review.product.name,
                'product_image': product_image,
                'product_category': review.product.category.name if review.product.category else '',
                'product_brand': review.product.brand.name if review.product.brand else '',
                'rating': review.rating,
                'comment': review.comment,
                'sentiment': review.sentiment,
                'sentiment_score': review.sentiment_score,
                'helpful_count': review.helpful_count,
                'is_approved': review.is_approved,
                'is_verified_purchase': review.is_verified_purchase,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'mismatch': mismatch_info.get('mismatch', False),
                'mismatch_message': mismatch_info.get('message', ''),
            }
        }

        return JsonResponse(data)


class ReviewDeleteView(StaffRequiredMixin, View):
    """Xóa đánh giá"""

    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        product = review.product
        review.delete()

        # Cập nhật sentiment stats cho product
        product.update_sentiment_stats()

        messages.success(request, 'Đã xóa đánh giá!')
        return redirect('admin_dashboard:review_list')


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


# ==================== Voucher Management ====================

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


# ==================== Flash Sale Management ====================

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


class FlashSaleBatchCreateView(StaffRequiredMixin, TemplateView):
    """Tạo flash sale hàng loạt với giao diện 2 cột"""
    template_name = 'admin_dashboard/promotions/flash_sale_batch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        return context

    def post(self, request):
        import json
        from decimal import Decimal

        product_ids = request.POST.getlist('product_ids')
        discount_percent = request.POST.get('discount_percent', 0)
        quantity_limit = request.POST.get('quantity_limit', 10)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not product_ids:
            messages.error(request, 'Vui lòng chọn ít nhất 1 sản phẩm!')
            return redirect('admin_dashboard:flash_sale_batch')

        try:
            discount_percent = int(discount_percent)
            quantity_limit = int(quantity_limit)

            from django.utils.dateparse import parse_datetime
            start_dt = parse_datetime(start_time)
            end_dt = parse_datetime(end_time)

            if not start_dt or not end_dt:
                messages.error(request, 'Thời gian không hợp lệ!')
                return redirect('admin_dashboard:flash_sale_batch')

            created_count = 0
            for pid in product_ids:
                try:
                    product = Product.objects.get(pk=pid)
                    FlashSale.objects.create(
                        product=product,
                        discount_type='percentage',
                        discount_percent=discount_percent,
                        quantity_limit=quantity_limit,
                        start_time=start_dt,
                        end_time=end_dt,
                        is_active=True
                    )
                    created_count += 1
                except Product.DoesNotExist:
                    continue

            messages.success(request, f'Tạo thành công {created_count} Flash Sale!')
            return redirect('admin_dashboard:flash_sale_list')

        except ValueError as e:
            messages.error(request, f'Dữ liệu không hợp lệ: {str(e)}')
            return redirect('admin_dashboard:flash_sale_batch')


# ==================== API Endpoints ====================

class ChartDataView(StaffRequiredMixin, View):
    """API endpoint cung cấp dữ liệu cho biểu đồ"""

    def get(self, request):
        chart_type = request.GET.get('type', 'revenue')
        period = request.GET.get('period', 'month')
        stats = DashboardStatistics()

        # Sử dụng timezone.now() để đồng bộ với created_at của orders
        today = timezone.now().date()
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == 'custom':
            start_str = request.GET.get('start_date')
            end_str = request.GET.get('end_date')
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                start_date = today.replace(day=1)
                end_date = today
        else:
            start_date = today.replace(day=1)
            end_date = today

        if chart_type == 'revenue':
            return JsonResponse(stats.get_daily_revenue_chart_data(start_date, end_date))
        elif chart_type == 'orders':
            return JsonResponse(stats.get_order_status_chart_data(start_date, end_date))
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


# ==================== Notifications ====================

class NotificationCreateView(StaffRequiredMixin, CreateView):
    """Tạo thông báo mới cho người dùng"""
    model = Notification
    form_class = NotificationForm
    template_name = 'admin_dashboard/notifications/form.html'
    success_url = reverse_lazy('admin_dashboard:notification_list')

    def form_valid(self, form):
        send_to = form.cleaned_data.get('send_to')
        users = form.cleaned_data.get('users')

        notification_type = form.cleaned_data.get('notification_type')
        title = form.cleaned_data.get('title')
        message = form.cleaned_data.get('message')
        url = form.cleaned_data.get('url', '')

        if send_to == 'all':
            target_users = User.objects.filter(is_active=True)
        else:
            target_users = users

        created_count = 0
        for user in target_users:
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                url=url
            )
            created_count += 1

        messages.success(self.request, f'Đã tạo {created_count} thông báo thành công!')
        return redirect(self.success_url)


class NotificationListView(StaffRequiredMixin, ListView):
    """Danh sách thông báo"""
    model = Notification
    template_name = 'admin_dashboard/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        queryset = Notification.objects.select_related('user').order_by('-created_at')

        notification_type = self.request.GET.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        is_read = self.request.GET.get('is_read')
        if is_read == '1':
            queryset = queryset.filter(is_read=True)
        elif is_read == '0':
            queryset = queryset.filter(is_read=False)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(message__icontains=search) | Q(user__username__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notification_types'] = Notification.NOTIFICATION_TYPES
        context['stats'] = {
            'total': Notification.objects.count(),
            'unread': Notification.objects.filter(is_read=False).count(),
        }
        return context


class NotificationDeleteView(StaffRequiredMixin, View):
    """Xóa thông báo"""

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.delete()
        messages.success(request, 'Đã xóa thông báo.')
        return redirect('admin_dashboard:notification_list')


class NotificationBulkActionView(StaffRequiredMixin, View):
    """Thao tác hàng loạt với thông báo"""

    def post(self, request):
        action = request.POST.get('action')
        notification_ids = request.POST.getlist('notification_ids')

        if not notification_ids:
            messages.warning(request, 'Vui lòng chọn ít nhất một thông báo.')
            return redirect('admin_dashboard:notification_list')

        notifications = Notification.objects.filter(pk__in=notification_ids)

        if action == 'mark_read':
            from django.utils import timezone
            notifications.update(is_read=True, read_at=timezone.now())
            messages.success(request, f'Đã đánh dấu {notifications.count()} thông báo đã đọc.')
        elif action == 'mark_unread':
            notifications.update(is_read=False, read_at=None)
            messages.success(request, f'Đã đánh dấu {notifications.count()} thông báo chưa đọc.')
        elif action == 'delete':
            count = notifications.count()
            notifications.delete()
            messages.success(request, f'Đã xóa {count} thông báo.')

        return redirect('admin_dashboard:notification_list')

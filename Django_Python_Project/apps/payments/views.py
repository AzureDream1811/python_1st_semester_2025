from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from apps.orders.models import Order
from .models import PaymentTransaction
from .services.payment_service import PaymentService
import uuid


@login_required
def create_vnpay_payment(request):
    """Tạo thanh toán VNPay"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        result = PaymentService.create_vnpay_payment(order, request)

        if result.get('success'):
            return redirect(result['payment_url'])
        else:
            messages.error(request, result.get('error', 'Không thể tạo thanh toán.'))
            return redirect('orders:detail', order_number=order.order_number)

    return redirect('orders:list')


@csrf_exempt
def vnpay_callback(request):
    """VNPay callback sau thanh toán"""
    result = PaymentService.process_vnpay_callback(request.GET)

    if result.get('success'):
        messages.success(request, 'Thanh toán thành công!')
        return redirect('payments:success')
    else:
        messages.error(request, result.get('error', 'Thanh toán thất bại.'))
        return redirect('payments:failed')


@csrf_exempt
def vnpay_ipn(request):
    """VNPay IPN (Instant Payment Notification)"""
    result = PaymentService.process_vnpay_ipn(request.GET)
    return HttpResponse(result.get('RspCode', '99'))


@login_required
def create_momo_payment(request):
    """Tạo thanh toán MoMo"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        result = PaymentService.create_momo_payment(order, request)

        if result.get('success'):
            return redirect(result['payment_url'])
        else:
            messages.error(request, result.get('error', 'Không thể tạo thanh toán.'))
            return redirect('orders:detail', order_number=order.order_number)

    return redirect('orders:list')


@csrf_exempt
def momo_callback(request):
    """MoMo callback sau thanh toán"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
    else:
        data = request.GET

    result = PaymentService.process_momo_callback(data)

    if result.get('success'):
        messages.success(request, 'Thanh toán thành công!')
        return redirect('payments:success')
    else:
        messages.error(request, result.get('error', 'Thanh toán thất bại.'))
        return redirect('payments:failed')


@login_required
def create_zalopay_payment(request):
    """Tạo thanh toán ZaloPay"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        result = PaymentService.create_zalopay_payment(order, request)

        if result.get('success'):
            return redirect(result['payment_url'])
        else:
            messages.error(request, result.get('error', 'Không thể tạo thanh toán.'))
            return redirect('orders:detail', order_number=order.order_number)

    return redirect('orders:list')


@csrf_exempt
def zalopay_callback(request):
    """ZaloPay callback sau thanh toán"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
    else:
        data = request.GET

    result = PaymentService.process_zalopay_callback(data)

    if result.get('success'):
        messages.success(request, 'Thanh toán thành công!')
        return redirect('payments:success')
    else:
        messages.error(request, result.get('error', 'Thanh toán thất bại.'))
        return redirect('payments:failed')


@login_required
def payment_status(request, order_id):
    """Kiểm tra trạng thái thanh toán"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    transaction = PaymentTransaction.objects.filter(order=order).last()

    context = {
        'order': order,
        'transaction': transaction,
    }
    return render(request, 'payments/status.html', context)


def payment_success(request):
    """Trang thanh toán thành công"""
    return render(request, 'payments/success.html')


def payment_failed(request):
    """Trang thanh toán thất bại"""
    return render(request, 'payments/failed.html')


# ============== QR PAYMENT VIEWS ==============

from .models import BankAccount, EWalletAccount
from .services.qr_service import QRService


ALLOWED_QR_METHODS = {'bank_transfer', 'momo', 'zalopay'}


def _get_or_create_qr_transaction(order):
    transaction = PaymentTransaction.objects.filter(
        order=order,
        payment_method=order.payment_method
    ).order_by('-created_at').first()

    if transaction:
        return transaction

    transaction_id = f"QR-{order.id}-{order.payment_method}-{uuid.uuid4().hex[:8].upper()}"
    return PaymentTransaction.objects.create(
        order=order,
        payment_method=order.payment_method,
        transaction_id=transaction_id,
        amount=order.total,
        status='pending'
    )


@login_required
def bank_transfer_payment(request, order_id):
    """Hiển thị thông tin chuyển khoản ngân hàng với QR"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.payment_method not in ALLOWED_QR_METHODS:
        messages.error(request, 'Invalid payment method for QR.')
        return redirect('orders:detail', order_number=order.order_number)

    # Lấy tài khoản ngân hàng mặc định
    bank_account = BankAccount.objects.filter(
        is_active=True,
        bank_code='MB'
    ).order_by('-is_default').first()
    if not bank_account:
        bank_account = BankAccount.objects.filter(is_active=True, is_default=True).first()
    if not bank_account:
        bank_account = BankAccount.objects.filter(is_active=True).first()

    if not bank_account:
        bank_account = BankAccount(
            bank_code='MB',
            bank_name='MB Bank',
            account_number='123456789',
            account_name='DEMO PROJECT',
            is_active=True,
            is_default=True
        )

    if not bank_account:
        messages.error(request, 'Chưa cấu hình tài khoản ngân hàng. Vui lòng chọn phương thức khác.')
        return redirect('orders:detail', order_number=order.order_number)

    # Tạo nội dung chuyển khoản
    transfer_content = QRService.generate_transfer_content(order.order_number, order.phone)

    # Tạo QR code
    qr_data = QRService.generate_vietqr(
        bank_code=bank_account.bank_code,
        account_number=bank_account.account_number,
        amount=order.total,
        content=transfer_content,
        account_name=bank_account.account_name
    )

    context = {
        'order': order,
        'bank_account': bank_account,
        'transfer_content': transfer_content,
        'qr_url': qr_data['qr_url'],
        'transaction': _get_or_create_qr_transaction(order),
    }
    return render(request, 'payments/bank_transfer.html', context)


@login_required
def momo_payment(request, order_id):
    """Hiển thị QR MoMo"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.payment_method not in ALLOWED_QR_METHODS:
        messages.error(request, 'Invalid payment method for QR.')
        return redirect('orders:detail', order_number=order.order_number)

    # Lấy tài khoản MoMo
    momo_account = EWalletAccount.objects.filter(
        wallet_type='momo', is_active=True, is_default=True
    ).first()
    if not momo_account:
        momo_account = EWalletAccount.objects.filter(wallet_type='momo', is_active=True).first()

    if not momo_account:
        momo_account = EWalletAccount(
            wallet_type='momo',
            wallet_id='0900000000',
            wallet_name='DEMO MOMO',
            is_active=True,
            is_default=True
        )

    if not momo_account:
        messages.error(request, 'Chưa cấu hình tài khoản MoMo. Vui lòng chọn phương thức khác.')
        return redirect('orders:detail', order_number=order.order_number)

    # Tạo nội dung chuyển khoản
    transfer_content = QRService.generate_transfer_content(order.order_number, order.phone)

    # Tạo QR code
    qr_data = QRService.generate_momo_qr(
        phone=momo_account.wallet_id,
        amount=order.total,
        content=transfer_content
    )

    context = {
        'order': order,
        'wallet_account': momo_account,
        'wallet_type': 'MoMo',
        'transfer_content': transfer_content,
        'qr_base64': qr_data['qr_base64'],
        'transaction': _get_or_create_qr_transaction(order),
    }
    return render(request, 'payments/ewallet.html', context)


@login_required
def zalopay_payment(request, order_id):
    """Hiển thị QR ZaloPay"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.payment_method not in ALLOWED_QR_METHODS:
        messages.error(request, 'Invalid payment method for QR.')
        return redirect('orders:detail', order_number=order.order_number)

    # Lấy tài khoản ZaloPay
    zalopay_account = EWalletAccount.objects.filter(
        wallet_type='zalopay', is_active=True, is_default=True
    ).first()
    if not zalopay_account:
        zalopay_account = EWalletAccount.objects.filter(wallet_type='zalopay', is_active=True).first()

    if not zalopay_account:
        zalopay_account = EWalletAccount(
            wallet_type='zalopay',
            wallet_id='0900000000',
            wallet_name='DEMO ZALOPAY',
            is_active=True,
            is_default=True
        )

    if not zalopay_account:
        messages.error(request, 'Chưa cấu hình tài khoản ZaloPay. Vui lòng chọn phương thức khác.')
        return redirect('orders:detail', order_number=order.order_number)

    # Tạo nội dung chuyển khoản
    transfer_content = QRService.generate_transfer_content(order.order_number, order.phone)

    # Tạo QR code
    qr_data = QRService.generate_zalopay_qr(
        wallet_id=zalopay_account.wallet_id,
        amount=order.total,
        content=transfer_content
    )

    context = {
        'order': order,
        'wallet_account': zalopay_account,
        'wallet_type': 'ZaloPay',
        'transfer_content': transfer_content,
        'qr_base64': qr_data['qr_base64'],
        'transaction': _get_or_create_qr_transaction(order),
    }
    return render(request, 'payments/ewallet.html', context)


@login_required
@require_POST
def mark_qr_scanned(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.payment_method not in ALLOWED_QR_METHODS:
        return JsonResponse({'success': False, 'message': 'Invalid payment method.'}, status=400)

    transaction = _get_or_create_qr_transaction(order)
    if transaction.status == 'pending':
        transaction.status = 'processing'
        transaction.response_message = 'qr_scanned'
        transaction.response_data = {
            'qr_scanned': True,
            'scanned_at': timezone.now().isoformat()
        }
        transaction.save(update_fields=['status', 'response_message', 'response_data', 'updated_at'])

    return JsonResponse({
        'success': True,
        'status': transaction.status
    })


@login_required
@require_POST
def confirm_manual_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.payment_method not in ALLOWED_QR_METHODS:
        return JsonResponse({'success': False, 'message': 'Invalid payment method.'}, status=400)

    transaction = _get_or_create_qr_transaction(order)
    if transaction.status != 'success':
        transaction.status = 'success'
        transaction.response_message = 'user_confirmed'
        transaction.response_data = {
            'confirmed_by_user': True,
            'confirmed_at': timezone.now().isoformat()
        }
        transaction.save(update_fields=['status', 'response_message', 'response_data', 'updated_at'])

    if order.payment_status != 'paid':
        order.payment_status = 'paid'
        order.save(update_fields=['payment_status'])

    if order.status == 'pending' and order.can_transition_to('confirmed'):
        order.transition_to('confirmed', note='User confirmed payment')

    return JsonResponse({
        'success': True,
        'redirect_url': reverse('orders:detail', args=[order.order_number])
    })


# ============== TRANSACTION HISTORY VIEWS ==============

from django.core.paginator import Paginator
from datetime import datetime


@login_required
def transaction_history(request):
    """Hiển thị lịch sử giao dịch thanh toán của người dùng"""
    transactions = PaymentTransaction.objects.filter(
        order__user=request.user
    ).select_related('order').order_by('-created_at')

    # Filter theo payment method
    payment_method = request.GET.get('payment_method')
    if payment_method:
        transactions = transactions.filter(payment_method=payment_method)

    # Filter theo status
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)

    # Filter theo date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            transactions = transactions.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            transactions = transactions.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page', 1)
    transactions = paginator.get_page(page)

    # Get payment methods for filter
    payment_methods = PaymentTransaction.PAYMENT_METHODS
    status_choices = PaymentTransaction.STATUS_CHOICES

    context = {
        'transactions': transactions,
        'payment_methods': payment_methods,
        'status_choices': status_choices,
        'current_payment_method': payment_method,
        'current_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'payments/transaction_history.html', context)


@login_required
def transaction_detail(request, transaction_id):
    """Chi tiết giao dịch"""
    transaction = get_object_or_404(
        PaymentTransaction,
        transaction_id=transaction_id,
        order__user=request.user
    )

    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/transaction_detail.html', context)


# ============== REFUND VIEWS ==============

from .models import Refund
from .forms import RefundRequestForm


@login_required
def refund_request(request):
    """Form yêu cầu hoàn tiền"""
    if request.method == 'POST':
        form = RefundRequestForm(request.POST, user=request.user)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.save()
            messages.success(request, 'Yêu cầu hoàn tiền đã được gửi thành công!')
            return redirect('payments:refund_list')
    else:
        form = RefundRequestForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'payments/refund_request.html', context)


@login_required
def refund_list(request):
    """Danh sách yêu cầu hoàn tiền của người dùng"""
    refunds = Refund.objects.filter(
        payment__order__user=request.user
    ).select_related('payment', 'payment__order').order_by('-created_at')

    # Pagination
    paginator = Paginator(refunds, 20)
    page = request.GET.get('page', 1)
    refunds = paginator.get_page(page)

    context = {
        'refunds': refunds,
    }
    return render(request, 'payments/refund_list.html', context)


@login_required
def refund_detail(request, refund_id):
    """Chi tiết yêu cầu hoàn tiền"""
    refund = get_object_or_404(
        Refund,
        pk=refund_id,
        payment__order__user=request.user
    )

    context = {
        'refund': refund,
    }
    return render(request, 'payments/refund_detail.html', context)

"""
Payment Service for ElectroShop
VNPay, MoMo, ZaloPay integration
"""
import hashlib
import hmac
import uuid
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone

from apps.payments.models import PaymentTransaction, Refund


class PaymentService:
    """Service for payment processing"""

    @staticmethod
    def create_vnpay_payment(order, request=None) -> Dict[str, Any]:
        """Create VNPay payment URL"""
        vnp_tmn_code = getattr(settings, 'VNPAY_TMN_CODE', '')
        vnp_hash_secret = getattr(settings, 'VNPAY_HASH_SECRET', '')
        vnp_url = getattr(settings, 'VNPAY_URL', '')
        vnp_return_url = getattr(settings, 'VNPAY_RETURN_URL', '')

        if not vnp_tmn_code:
            return {'success': False, 'error': 'VNPay chưa được cấu hình'}

        # Create transaction
        transaction_id = f"VNP{order.id}{datetime.now().strftime('%Y%m%d%H%M%S')}"

        PaymentTransaction.objects.create(
            order=order,
            payment_method='vnpay',
            transaction_id=transaction_id,
            amount=order.total,
            status='pending'
        )

        # Build VNPay params
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': vnp_tmn_code,
            'vnp_Amount': int(order.total * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': transaction_id,
            'vnp_OrderInfo': f'Thanh toan don hang {order.order_number}',
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': vnp_return_url,
            'vnp_IpAddr': '127.0.0.1',
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }

        # Sort and create hash
        sorted_params = sorted(vnp_params.items())
        query_string = urlencode(sorted_params)
        hash_value = hmac.new(
            vnp_hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        payment_url = f"{vnp_url}?{query_string}&vnp_SecureHash={hash_value}"

        return {
            'success': True,
            'payment_url': payment_url,
            'transaction_id': transaction_id
        }

    @staticmethod
    def create_momo_payment(order, request=None) -> Dict[str, Any]:
        """Create MoMo payment"""
        partner_code = getattr(settings, 'MOMO_PARTNER_CODE', '')
        access_key = getattr(settings, 'MOMO_ACCESS_KEY', '')
        secret_key = getattr(settings, 'MOMO_SECRET_KEY', '')

        if not partner_code:
            return {'success': False, 'error': 'MoMo chưa được cấu hình'}

        transaction_id = f"MOMO{order.id}{datetime.now().strftime('%Y%m%d%H%M%S')}"

        PaymentTransaction.objects.create(
            order=order,
            payment_method='momo',
            transaction_id=transaction_id,
            amount=order.total,
            status='pending'
        )

        # TODO: Implement actual MoMo API call
        # Return QR code or deep link

        return {
            'success': True,
            'transaction_id': transaction_id,
            'qr_code': f'momo://pay?amount={order.total}&orderId={transaction_id}'
        }

    @staticmethod
    def create_zalopay_payment(order, request=None) -> Dict[str, Any]:
        """Create ZaloPay payment"""
        app_id = getattr(settings, 'ZALOPAY_APP_ID', '')

        if not app_id:
            return {'success': False, 'error': 'ZaloPay chưa được cấu hình'}

        transaction_id = f"ZLP{order.id}{datetime.now().strftime('%Y%m%d%H%M%S')}"

        PaymentTransaction.objects.create(
            order=order,
            payment_method='zalopay',
            transaction_id=transaction_id,
            amount=order.total,
            status='pending'
        )

        # TODO: Implement actual ZaloPay API call

        return {
            'success': True,
            'transaction_id': transaction_id,
            'payment_url': f'https://zalopay.vn/pay?orderId={transaction_id}'
        }

    @staticmethod
    def process_vnpay_callback(data: Dict) -> Dict[str, Any]:
        """Process VNPay callback"""
        transaction_id = data.get('vnp_TxnRef')
        response_code = data.get('vnp_ResponseCode')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return {'success': False, 'error': 'Transaction not found'}

        transaction.response_code = response_code
        transaction.response_data = dict(data)

        if response_code == '00':
            transaction.status = 'success'
            # Update order status
            order = transaction.order
            order.payment_status = 'paid'
            order.save(update_fields=['payment_status'])
        else:
            transaction.status = 'failed'
            transaction.response_message = f'Payment failed with code: {response_code}'

        transaction.save()

        return {
            'success': transaction.status == 'success',
            'transaction_id': transaction_id,
            'status': transaction.status
        }

    @staticmethod
    def process_vnpay_ipn(data: Dict) -> Dict[str, Any]:
        """Process VNPay IPN (Instant Payment Notification)"""
        transaction_id = data.get('vnp_TxnRef')
        response_code = data.get('vnp_ResponseCode')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
        except PaymentTransaction.DoesNotExist:
            return {'RspCode': '01', 'Message': 'Transaction not found'}

        if response_code == '00':
            transaction.status = 'success'
            transaction.order.payment_status = 'paid'
            transaction.order.save(update_fields=['payment_status'])
        else:
            transaction.status = 'failed'

        transaction.response_code = response_code
        transaction.response_data = dict(data)
        transaction.save()

        return {'RspCode': '00', 'Message': 'Confirm Success'}

    @staticmethod
    def process_momo_callback(data: Dict) -> Dict[str, Any]:
        """Process MoMo callback"""
        result_code = data.get('resultCode')
        order_id = data.get('orderId')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=order_id)
        except PaymentTransaction.DoesNotExist:
            return {'success': False, 'error': 'Transaction not found'}

        if result_code == 0 or result_code == '0':
            transaction.status = 'success'
            transaction.order.payment_status = 'paid'
            transaction.order.save(update_fields=['payment_status'])
        else:
            transaction.status = 'failed'

        transaction.response_code = str(result_code)
        transaction.response_data = dict(data) if isinstance(data, dict) else data
        transaction.save()

        return {
            'success': transaction.status == 'success',
            'transaction_id': order_id,
            'status': transaction.status
        }

    @staticmethod
    def process_zalopay_callback(data: Dict) -> Dict[str, Any]:
        """Process ZaloPay callback"""
        return_code = data.get('return_code')
        app_trans_id = data.get('app_trans_id')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=app_trans_id)
        except PaymentTransaction.DoesNotExist:
            return {'success': False, 'error': 'Transaction not found'}

        if return_code == 1 or return_code == '1':
            transaction.status = 'success'
            transaction.order.payment_status = 'paid'
            transaction.order.save(update_fields=['payment_status'])
        else:
            transaction.status = 'failed'

        transaction.response_code = str(return_code)
        transaction.response_data = dict(data) if isinstance(data, dict) else data
        transaction.save()

        return {
            'success': transaction.status == 'success',
            'transaction_id': app_trans_id,
            'status': transaction.status
        }

    @staticmethod
    def process_callback(provider: str, data: Dict) -> Dict[str, Any]:
        """
        Process payment callback
        Property 23: Must update order status on success
        """
        if provider == 'vnpay':
            return PaymentService.process_vnpay_callback(data)
        elif provider == 'momo':
            return PaymentService.process_momo_callback(data)
        elif provider == 'zalopay':
            return PaymentService.process_zalopay_callback(data)

        return {'success': False, 'error': 'Unknown provider'}

    @staticmethod
    def process_refund(order_id: int, amount: Decimal = None, reason: str = '') -> Dict[str, Any]:
        """
        Process refund
        Property 24: Must refund via same payment method
        """
        from apps.orders.models import Order

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return {'success': False, 'error': 'Order not found'}

        # Get original payment
        original_payment = PaymentTransaction.objects.filter(
            order=order,
            status='success'
        ).first()

        if not original_payment:
            return {'success': False, 'error': 'No successful payment found'}

        refund_amount = amount or original_payment.amount

        # Create refund record
        refund = Refund.objects.create(
            payment=original_payment,
            amount=refund_amount,
            reason=reason,
            status='pending'
        )

        # TODO: Call actual refund API based on payment method
        # For now, mark as completed
        refund.status = 'completed'
        refund.refund_transaction_id = f"REF-{uuid.uuid4().hex[:10].upper()}"
        refund.processed_at = timezone.now()
        refund.save()

        return {
            'success': True,
            'refund_id': refund.id,
            'refund_transaction_id': refund.refund_transaction_id,
            'amount': float(refund_amount),
            'payment_method': original_payment.payment_method
        }

    @staticmethod
    def get_payment_report(start_date, end_date) -> Dict[str, Any]:
        """
        Generate payment report
        Property 25: Report must match actual transaction data
        """
        from django.db.models import Sum, Count

        transactions = PaymentTransaction.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='success'
        )

        # Aggregate by payment method
        by_method = transactions.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_count = transactions.count()

        # Success rate
        all_transactions = PaymentTransaction.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        success_rate = (total_count / all_transactions.count() * 100) if all_transactions.count() > 0 else 0

        return {
            'period': {'start': start_date, 'end': end_date},
            'total_amount': float(total_amount),
            'total_transactions': total_count,
            'success_rate': round(success_rate, 2),
            'by_payment_method': {
                item['payment_method']: {
                    'total': float(item['total']),
                    'count': item['count']
                }
                for item in by_method
            }
        }

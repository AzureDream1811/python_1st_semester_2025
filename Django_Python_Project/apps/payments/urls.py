from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # VNPay
    path('vnpay/create/', views.create_vnpay_payment, name='vnpay_create'),
    path('vnpay/callback/', views.vnpay_callback, name='vnpay_callback'),
    path('vnpay/ipn/', views.vnpay_ipn, name='vnpay_ipn'),

    # MoMo
    path('momo/create/', views.create_momo_payment, name='momo_create'),
    path('momo/callback/', views.momo_callback, name='momo_callback'),

    # ZaloPay
    path('zalopay/create/', views.create_zalopay_payment, name='zalopay_create'),
    path('zalopay/callback/', views.zalopay_callback, name='zalopay_callback'),

    # QR Payment Pages
    path('bank-transfer/<int:order_id>/', views.bank_transfer_payment, name='bank_transfer'),
    path('momo/<int:order_id>/', views.momo_payment, name='momo_payment'),
    path('zalopay/<int:order_id>/', views.zalopay_payment, name='zalopay_payment'),
    path('qr-scan/<int:order_id>/', views.mark_qr_scanned, name='qr_scan'),
    path('confirm/<int:order_id>/', views.confirm_manual_payment, name='confirm_manual_payment'),

    # Transaction History
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transactions/<str:transaction_id>/', views.transaction_detail, name='transaction_detail'),

    # Refund
    path('refunds/', views.refund_list, name='refund_list'),
    path('refunds/request/', views.refund_request, name='refund_request'),
    path('refunds/<int:refund_id>/', views.refund_detail, name='refund_detail'),

    # General
    path('status/<int:order_id>/', views.payment_status, name='status'),
    path('success/', views.payment_success, name='success'),
    path('failed/', views.payment_failed, name='failed'),
]

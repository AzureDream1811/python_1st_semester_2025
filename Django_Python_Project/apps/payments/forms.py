"""
Forms cho Payments App
"""
from django import forms
from .models import PaymentTransaction, Refund


class RefundRequestForm(forms.ModelForm):
    """Form yêu cầu hoàn tiền"""

    class Meta:
        model = Refund
        fields = ['payment', 'amount', 'reason']
        widgets = {
            'payment': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'step': '1000',
                'placeholder': 'Nhập số tiền cần hoàn',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Nhập lý do yêu cầu hoàn tiền...',
                'required': True
            }),
        }
        labels = {
            'payment': 'Giao dịch cần hoàn',
            'amount': 'Số tiền hoàn (VNĐ)',
            'reason': 'Lý do hoàn tiền',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter payments to only show user's successful transactions
        if user:
            self.fields['payment'].queryset = PaymentTransaction.objects.filter(
                order__user=user,
                status='success'
            ).select_related('order').order_by('-created_at')

            # Custom label for payment choices
            self.fields['payment'].label_from_instance = lambda obj: (
                f"#{obj.order.order_number} - {obj.amount:,.0f}₫ ({obj.get_payment_method_display()})"
            )

    def clean_amount(self):
        """Validate số tiền hoàn không vượt quá số tiền giao dịch"""
        amount = self.cleaned_data.get('amount')
        payment = self.cleaned_data.get('payment')

        if amount and amount <= 0:
            raise forms.ValidationError('Số tiền hoàn phải lớn hơn 0')

        if payment and amount:
            # Tính tổng số tiền đã hoàn cho giao dịch này
            total_refunded = Refund.objects.filter(
                payment=payment,
                status__in=['pending', 'processing', 'completed']
            ).exclude(pk=self.instance.pk if self.instance.pk else None).aggregate(
                total=forms.models.Sum('amount')
            )['total'] or 0

            remaining = payment.amount - total_refunded

            if amount > remaining:
                raise forms.ValidationError(
                    f'Số tiền hoàn không được vượt quá số tiền còn lại ({remaining:,.0f}₫)'
                )

        return amount

    def clean_reason(self):
        """Validate lý do không được để trống"""
        reason = self.cleaned_data.get('reason')

        if not reason or not reason.strip():
            raise forms.ValidationError('Vui lòng nhập lý do hoàn tiền')

        if len(reason.strip()) < 10:
            raise forms.ValidationError('Lý do hoàn tiền phải có ít nhất 10 ký tự')

        return reason.strip()

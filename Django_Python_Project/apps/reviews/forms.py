from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form viết đánh giá sản phẩm với sentiment analysis"""

    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image1', 'image2', 'image3']
        labels = {
            'rating': 'Đánh giá sao',
            'comment': 'Nội dung đánh giá',
            'image1': 'Hình ảnh 1',
            'image2': 'Hình ảnh 2',
            'image3': 'Hình ảnh 3',
        }
        widgets = {
            'rating': forms.RadioSelect(
                attrs={
                    'class': 'rating-input'
                },
                choices=Review.RATING_CHOICES
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Chia sẻ trải nghiệm của bạn về sản phẩm này...\n\nVí dụ: Sản phẩm chất lượng tốt, giao hàng nhanh, đóng gói cẩn thận...',
                'rows': 5,
                'minlength': 10,
            }),
            'image1': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image2': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image3': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        error_messages = {
            'rating': {
                'required': 'Vui lòng chọn số sao đánh giá',
            },
            'comment': {
                'required': 'Vui lòng nhập nội dung đánh giá',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đặt rating là required
        self.fields['rating'].required = True
        self.fields['comment'].required = True
        # Hình ảnh không bắt buộc
        self.fields['image1'].required = False
        self.fields['image2'].required = False
        self.fields['image3'].required = False

    def clean_comment(self):
        """Validate nội dung đánh giá"""
        comment = self.cleaned_data.get('comment')
        if comment:
            # Kiểm tra độ dài tối thiểu
            if len(comment.strip()) < 10:
                raise forms.ValidationError('Nội dung đánh giá phải có ít nhất 10 ký tự')
            # Kiểm tra độ dài tối đa
            if len(comment) > 2000:
                raise forms.ValidationError('Nội dung đánh giá không được quá 2000 ký tự')
        return comment.strip() if comment else comment

    def clean_rating(self):
        """Validate số sao đánh giá"""
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError('Vui lòng chọn số sao đánh giá')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Số sao phải từ 1 đến 5')
        return rating

    def clean(self):
        """Validate tổng thể form"""
        cleaned_data = super().clean()
        # Có thể thêm validation cross-field ở đây
        return cleaned_data

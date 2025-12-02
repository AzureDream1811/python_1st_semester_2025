from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form viết đánh giá"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'image1', 'image2', 'image3']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'rating-input'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiêu đề đánh giá (không bắt buộc)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Chia sẻ trải nghiệm của bạn về sản phẩm...',
                'rows': 5
            }),
            'image1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment) < 10:
            raise forms.ValidationError('Nội dung đánh giá phải có ít nhất 10 ký tự')
        return comment

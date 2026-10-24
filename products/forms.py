from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(value, str(value)) for value in range(1, 6)],
        coerce=int,
        widget=forms.RadioSelect,
        label='Đánh giá',
    )

    class Meta:
        model = ProductReview
        fields = ('rating', 'content')
        labels = {'rating': 'Đánh giá', 'content': 'Nhận xét'}
        widgets = {
            'rating': forms.RadioSelect,
            'content': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 2000,
                'placeholder': 'Chia sẻ cảm nhận của bạn về sản phẩm…',
            }),
        }

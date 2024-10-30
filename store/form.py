from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "Choose Category"


class NewsletterForm(forms.Form):
    subject = forms.CharField(max_length=255, required=True, label="Newsletter Subject")
    heading = forms.CharField(max_length=255, required=True, label="Newsletter Heading")
    message = forms.CharField(
        widget=forms.Textarea, required=True, label="Newsletter Content"
    )
    url = forms.URLField(required=False, label="Call to Action URL (Optional)")


payment_choices = (
    ("paypal", "paypal"),
    ("paystack", "paystack"),
)


class OrderFilterForm(forms.Form):
    order_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "date-picker", "type": "date"})
    )


class UserProfileForm(UserChangeForm):
    password = None  # Exclude the password field

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone_number", "country"]


class CustomerRatingForm(forms.ModelForm):
    class Meta:
        model = CustomerRating
        fields = ["rating", "headline", "review"]
        widgets = {
            "rating": forms.Select(
                choices=[
                    (1, "★☆☆☆☆"),
                    (2, "★★☆☆☆"),
                    (3, "★★★☆☆"),
                    (4, "★★★★☆"),
                    (5, "★★★★★"),
                ],
                attrs={
                    "class": "star-rating-select",  # Updated class for styling
                    "aria-label": "Select rating",
                    "id": "star-rating",
                },
            ),
            "headline": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Headline",
                    "aria-label": "Headline",
                }
            ),
            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your review here...",
                    "rows": 4,
                    "aria-label": "Review",
                }
            ),
        }
        labels = {
            "rating": "Rating",
            "headline": "Headline",
            "review": "Review",
        }


class CouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs=(
                {
                    "class": "form-control",
                    "placeholder": "Have a coupon? Click here to enter your code",
                }
            )
        ),
        max_length=10,
    )


class RefundRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs=({"class": "form-control", "required": True, "placeholder": "email"})
        )
    )
    reference_code = forms.CharField(
        widget=forms.TextInput(
            attrs=(
                {
                    "class": "form-control",
                    "required": True,
                    "placeholder": "order reference",
                }
            )
        ),
        max_length=15,
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs=(
                {
                    "class": "form-control",
                    "required": True,
                    "placeholder": "reason for refund",
                }
            )
        ),
        max_length=1000,
    )


class CartUpdateForm(forms.Form):
    pk = forms.IntegerField()
    size = forms.CharField(max_length=15)
    quantity = forms.IntegerField()

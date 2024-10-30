from .models import DeliveryLocations
from django import forms
from store.models import CustomersAddress
from phonenumber_field.modelfields import PhoneNumberField
from store.models import Profile
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class VerifyPhoneForm(forms.ModelForm):
    country = CountryField().formfield(
        widget=CountrySelectWidget(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = Profile
        fields = ["phone_number", "country"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone_number"].widget = forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your phone number",
            }
        )


class LocationForm(forms.ModelForm):
    class Meta:
        model = DeliveryLocations
        fields = ["state"]

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        locations = DeliveryLocations.objects.all()
        location_choices = [(location.id, location.state) for location in locations]
        self.fields["state"].widget = forms.Select(
            choices=location_choices, attrs={"class": "form-control"}
        )


class PhoneNumberForm(forms.Form):
    phone_number = PhoneNumberField(region="NG")  # Initialize without widget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the custom widget for phone_number here
        self.fields["phone_number"].widget = forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter phone number"}
        )

        # Set the label
        self.fields["phone_number"].label = "Phone Number"


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
    )


# class AddressForm(forms.ModelForm):
#     class Meta:
#         model = CustomersAddress
#         fields = ['street_address', 'apartment', 'town', 'state', 'telephone', 'zip_code', 'country', 'message']
#         widgets = {
#             'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
#             'apartment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nearby landmark'}),
#             'town': forms.Select(attrs={'class': 'form-control', 'id': 'id_town'}),
#             'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
#             'state': forms.Select(attrs={'class': 'form-control', 'id': 'state-select'}),
#             'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+2348099999999'}),
#             'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
#             'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Do you have any message about your delivery? (optional)'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super(AddressForm, self).__init__(*args, **kwargs)
#         # Get distinct states
#         abuja_states = DeliveryLocations.objects.values('state').distinct()
#         self.fields['state'].choices = [(state['state'], state['state']) for state in abuja_states]
#         self.fields['town'].choices = []  # Initially empty until state is selected
#         # self.fields['town'].widget.attrs.update({'id': 'id_town'})


from django_countries.widgets import CountrySelectWidget


class AddressForm(forms.ModelForm):
    class Meta:
        model = CustomersAddress
        fields = [
            "street_address",
            "apartment",
            "town",
            "state",
            "telephone",
            "zip_code",
            "country",
            "message",
        ]
        widgets = {
            "street_address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Street Address"}
            ),
            "apartment": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nearby landmark"}
            ),
            "town": forms.Select(attrs={"class": "form-control", "id": "id_town"}),
            "zip_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Zip Code"}
            ),
            "state": forms.Select(
                attrs={"class": "form-control", "id": "state-select"}
            ),
            "telephone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+2348099999999"}
            ),
            "country": CountrySelectWidget(
                attrs={"class": "form-control"}
            ),  # Use CountrySelectWidget
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Do you have any message about your delivery? (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        # Populate states and town choices
        abuja_states = DeliveryLocations.objects.values("state").distinct()
        self.fields["state"].choices = [
            (state["state"], state["state"]) for state in abuja_states
        ]
        self.fields["town"].choices = []

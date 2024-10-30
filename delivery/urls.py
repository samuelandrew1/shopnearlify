from django.urls import path
from . import views

app_name = "delivery"


urlpatterns = [
    path(
        "update-delivery-cost/", views.update_delivery_cost, name="update_delivery_cost"
    ),
    path(
        "verify-phone/get-otp",
        views.PhoneNumberView.as_view(),
        name="phone_number_verify",
    ),
    path("verify-phone/verify-otp", views.verify_otp, name="verify_otp"),
]

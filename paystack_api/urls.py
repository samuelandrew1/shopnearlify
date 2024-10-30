from django.urls import path
from . import views

app_name = "paystack"

urlpatterns = [
    path("order/payment/", views.initiate_payment, name="initiate_payment"),
    path("verify-payment/<str:ref>/", views.verify_payment, name="verify_payment"),
]

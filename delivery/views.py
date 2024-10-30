from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from store.models import Order
from delivery.models import DeliveryLocations

from twilio.rest import Client
from django.conf import settings
from store.models import Profile
from .deliveryform import PhoneNumberForm, OTPForm, VerifyPhoneForm
from django.shortcuts import redirect, render
from twilio.rest import Client

# from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from shopnearlify import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from twilio.base.exceptions import TwilioRestException


import random


def generate_otp():
    return str(random.randint(100000, 999999))


@csrf_exempt
@require_POST
def update_delivery_cost(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        state = request.POST.get("state")
        town = request.POST.get("town")

        try:
            order = Order.objects.get(user=request.user, is_ordered=False)
            delivery_location = DeliveryLocations.objects.get(
                state=state, town_name=town
            )

            # Calculate delivery cost and update the order's delivery location
            delivery_cost = delivery_location.delivery_cost
            order.delivery_location = delivery_location
            order.save()

            # Calculate the total with delivery
            total_with_delivery = (
                order.get_total_with_delivery()
            )  # Assuming you have a method for this

            response_data = {
                "success": True,
                "total_with_delivery": total_with_delivery,
                "delivery_cost": delivery_cost,
            }
        except (Order.DoesNotExist, DeliveryLocations.DoesNotExist):
            response_data = {
                "success": False,
                "error": "Invalid state or town, or no active order found.",
            }
        return JsonResponse(response_data)
    return JsonResponse({"success": False, "error": "Invalid request method."})


@method_decorator(login_required, name="dispatch")
class PhoneNumberView(View):
    def get(self, request, *args, **kwargs):
        phone_form = VerifyPhoneForm()
        return render(request, "store/verify_phone_number.html", {"form": phone_form})

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            phone_number = self.request.POST.get("phone_number")
            country_code = self.request.POST.get("country")
            otp_code = generate_otp()

            full_phone_number = f"{country_code}{phone_number}"

            try:
                # Initialize Twilio client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

                # Send OTP via Twilio SMS
                message = client.messages.create(
                    body=f"Your verification code is {otp_code}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=full_phone_number,
                )
            except TwilioRestException as e:
                return JsonResponse({"status": f"Failed to send OTP: {e}"})

            # Save the OTP in session for later verification
            request.session["otp_code"] = otp_code
            request.session.modified = True

            return JsonResponse({"status": "OTP sent successfully"})

        return render(request, "store/verify_phone_number.html")


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp_code")
        session_otp = request.session.get("otp_code")

        if user_otp == session_otp:
            return JsonResponse({"status": "Phone number verified"})
        else:
            return JsonResponse({"status": "Invalid OTP"})
    return render(request, "store/verify_otp.html")

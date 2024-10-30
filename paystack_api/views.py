from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
import requests
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from shopnearlify import settings
from store.models import Cart, CustomersAddress, Invoice, Order, Payment
from store.views import create_ref_code, generate_random_number
from django.db.models import F

# Create your views here.
from store.models import Notifications


def initiate_payment(request):
    order = Order.objects.get(is_ordered=False, user=request.user)
    cart = Cart.objects.filter(user=request.user, is_ordered=False)

    if request.method == "POST":
        amount = request.POST["amount"]
        email = request.POST["email"]
        pk = settings.PAYSTACK_PUBLIC_KEY

        # Convert amount to float instead of int
        payment = Payment.objects.create(
            amount=float(amount), email=email, order=order, user=request.user
        )
        payment.save()

        context = {
            "payment": payment,
            "field_values": request.POST,
            "paystack_pub_key": pk,
            "amount_value": payment.amount_value(),
            "order": order,
            "cart": cart,
        }

        return render(request, "store/make-payment.html", context)

    return render(request, "store/payment.html", {"order": order, "cart": cart})


import logging
import sys

# Ensure UTF-8 encoding for stdout (prints) if using prints instead of logging
sys.stdout.reconfigure(encoding="utf-8")

# Use logging instead of print statements
logger = logging.getLogger(__name__)


def verify_payment(request, ref):
    try:
        order = Order.objects.get(is_ordered=False, user=request.user)
        payment = Payment.objects.get(ref=ref)
        address = CustomersAddress.objects.get(user=request.user)
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        verify_url = f"https://api.paystack.co/transaction/verify/{ref}"
        headers = {
            "Authorization": f"Bearer {paystack_secret_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(verify_url, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            paystack_amount = data["data"]["amount"] / 100  # Convert kobo to naira
            expected_amount = order.get_total_with_delivery()

            if (
                paystack_amount == expected_amount
                and data["data"]["status"] == "success"
            ):
                payment.verified = True
                payment.save()

                # Update stock and quantity sold for each product in the order
                for order_product in order.product.all():
                    product = order_product.product
                    quantity = order_product.quantity

                    # Update stock in Color model if color exists
                    if order_product.color:
                        product_size = order_product.size
                        product_color = order_product.color
                        product_color.stock = F("stock") - product_size.pieces
                        product_color.save()

                    # Update quantity sold in Size model if size exists
                    if order_product.size:
                        product_size = order_product.size
                        product_size.quantity_sold = F("quantity_sold") + quantity
                        product_size.save()

                    # Update product quantity sold
                    product.quantity_sold = F("quantity_sold") + quantity
                    product.save()

                # Mark order products as ordered
                order_products = order.product.all()
                order_products.update(is_ordered=True)

                # Update order status and create invoice
                order.is_ordered = True
                order.payment = payment
                order.reference = create_ref_code()  # create a reference code
                order.save()

                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_number=generate_random_number(),  # function for generating invoice numbers
                    order=order,
                    payment=payment,
                    issued_at=timezone.datetime.now(),
                    # Add more fields as needed
                )
                invoice.save()

                # Save additional invoice details
                order.invoice_number = invoice.invoice_number
                order.shipping_address = address
                order.save()
                notifications = Notifications.objects.create(
                    title="you have a new order from {}".format(request.user),
                    date=timezone.datetime.now(),
                    seen=False,
                )
                notifications.save()

                # Prepare and send the success email
                subject = "Payment Successful"
                html_message = render_to_string(
                    "emails/payment_success.html",
                    {"invoice": invoice, "order": order, "payment": payment},
                )
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = request.user.email

                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [to_email],
                    html_message=html_message,
                )

                # Prepare and send the success email
                subject = f"payment alert!"

                # Notify the admin about the payment
                admin_email = settings.ADMIN_EMAIL
                admin_subject = f"Payment Verified for Order {order.id}"
                admin_html_message = render_to_string(
                    "emails/admin_payment_notification.html",
                    {
                        "invoice": invoice,
                        "order": order,
                        "payment": payment,
                    },
                )
                admin_plain_message = strip_tags(admin_html_message)

                send_mail(
                    admin_subject,
                    admin_plain_message,
                    from_email,
                    [admin_email],
                    html_message=admin_html_message,
                )

                return render(
                    request,
                    "store/success.html",
                    {"invoice": invoice, "order": order, "payment": payment},
                )
            else:
                # Prepare and send the failure email
                subject = "Payment Not Successful"
                message = "Your payment could not be processed. Please try again or contact support."
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = request.user.email

                send_mail(subject, message, from_email, [to_email])

                return render(request, "emails/payment_not_successful.html")

        else:
            logger.error(
                f"Failed to verify payment. Status code: {response.status_code}, Paystack response: {response.text}"
            )
            return JsonResponse(
                {"status": "error", "message": "Failed to verify payment."}
            )

    except Order.DoesNotExist:
        logger.error("Order does not exist for the user.")
        return JsonResponse(
            {"status": "error", "message": "Order does not exist for the user."}
        )
    except Payment.DoesNotExist:
        logger.error("Payment does not exist for the reference.")
        return JsonResponse(
            {"status": "error", "message": "Payment does not exist for the reference."}
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return JsonResponse(
            {"status": "error", "message": f"Error verifying payment: {str(e)}"}
        )

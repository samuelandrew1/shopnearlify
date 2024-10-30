from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html
import io

from .models import *
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import path
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import Order
from xhtml2pdf import pisa
import io
from django.shortcuts import get_object_or_404
from .form import NewsletterForm
from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from .models import EmailSubscription
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
import datetime
from django.shortcuts import redirect
from django.utils.timezone import now
from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.db.models import Q


from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse


def send_invoice(request, order_id, *args, **kwargs):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            # order_id = request.POST.get('order_id')
            order = Order.objects.get(id=order_id)
            invoice = get_object_or_404(Invoice, order=order)
            subject = f"Invoice for Order {order.reference}"

            # Render the email message
            message = render_to_string(
                "store/send_invoice.html", {"order": order, "invoice": invoice}
            )

            # Send the email
            email = EmailMessage(subject, message, to=[order.user.email])
            email.content_subtype = "html"
            email.send()

            # Send JSON response indicating success
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Invoice for order {order.reference} sent successfully.",
                }
            )

        except Order.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Order does not exist."}, status=400
            )

        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Error sending invoice: {e}"},
                status=500,
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request."}, status=400
        )


class Invoice(View):
    def post(self, request, *args, **kwargs):
        next_url = request.GET.get("next")
        if request.method == "POST":
            order_id = request.POST.get("order_id")
            try:
                order = Order.objects.get(id=order_id)
                invoice = get_object_or_404(Invoice, order=order)
                subject = f"Invoice for Order {order.reference}"
                message = render_to_string(
                    "store/send_invoice.html", {"order": order, "invoice": invoice}
                )
                email = EmailMessage(subject, message, to=[order.user.email])
                email.content_subtype = "html"
                email.send()
                self.message_user(
                    request, f"Invoice for order {order.reference} sent successfully."
                )
            except Order.DoesNotExist:
                self.message_user(
                    request, "Order does not exist.", level=messages.ERROR
                )
            except Exception as e:
                self.message_user(
                    request, f"Error sending invoice: {e}", level=messages.ERROR
                )
                if next_url and url_has_allowed_host_and_scheme(
                    next_url, allowed_hosts={request.get_host()}
                ):
                    return redirect(next_url)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            # return redirect("store:index")

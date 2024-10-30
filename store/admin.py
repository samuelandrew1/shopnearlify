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

# admin.py
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.core.paginator import Paginator
from django.utils.html import format_html
from django.contrib import admin, messages
from .models import *
from .form import ProductForm
from django.template.exceptions import TemplateDoesNotExist
from django.utils.http import url_has_allowed_host_and_scheme


class BaseAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["home_page_link"] = True  # Flag to show the homepage link
        return super().changelist_view(request, extra_context=extra_context)


def send_newsletter(modeladmin, request, queryset):
    email_list = [subscriber.email for subscriber in queryset]

    # Initialize form with POST data if present, otherwise create an empty form
    form = NewsletterForm(request.POST or None)

    if "apply" in request.POST:  # Check if the form was submitted
        if form.is_valid():
            print("Form is valid")  # Debug: Ensure this is printed
            subject = form.cleaned_data["subject"]
            heading = form.cleaned_data["heading"]
            message = form.cleaned_data["message"]
            url = form.cleaned_data["url"]

            if email_list:
                try:
                    print("Preparing email...")  # Debug message

                    # Context for the email template
                    context = {
                        "heading": heading,
                        "subject": subject,
                        "message": message,
                        "url": (
                            url if url else "https://yourwebsite.com/newsletter"
                        ),  # Optional default URL
                        "year": datetime.datetime.now().year,
                    }

                    # Render the HTML template
                    html_content = render_to_string(
                        "emails/newsletter_email.html", context
                    )
                    text_content = strip_tags(html_content)

                    # Create an email message
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=email_list,
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send(fail_silently=False)

                    print("Email sent")  # Debug message

                    messages.success(
                        request,
                        f"Successfully sent emails to {len(email_list)} subscribers.",
                    )
                except Exception as e:
                    print(f"Error: {e}")  # Debug the error
                    messages.error(request, f"An error occurred: {e}")
                else:
                    messages.error(request, "No subscribers selected.")
                return redirect(request.get_full_path())

    # If the form wasn't submitted or wasn't valid, render the form
    return render(
        request, "admin/newsletter_form.html", {"form": form, "subscribers": queryset}
    )


# Customize the EmailSubscriptionAdmin to include the action
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "date")  # Customize the list display as needed
    actions = [send_newsletter]  # Add the send_newsletter function as an action


# Register the model with the custom admin class
admin.site.register(EmailSubscription, EmailSubscriptionAdmin)


class ProductFilter(admin.SimpleListFilter):
    title = _("product")  # Filter title
    parameter_name = "product"  # Query string parameter name

    def lookups(self, request, model_admin):
        # List of products to filter by (returning id and name)
        products = Product.objects.all()
        return [(product.id, product.title) for product in products]

    def queryset(self, request, queryset):
        # Filter queryset based on selected product
        if self.value():
            return queryset.filter(items__product__id=self.value())
        return queryset


from store.models import Notifications
from django.http import JsonResponse


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ["title", "image_tag", "total_stock"]
    # change_list_template = 'admin/product/change_list.html'
    raw_id_fields = ["category"]
    raw_id_fields = ["size"]

    def image_tag(self, obj):
        return format_html(
            '<img src="{}" style="max-width:50px; max-height:100px"/>'.format(
                obj.img_1.url
            )
        )

    image_tag.short_description = "Image"

    # Override changelist_view to handle creation and listing
    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Product created successfully.")
                return redirect(request.path_info)
        else:
            form = ProductForm()

        queryset = self.get_queryset(request)
        paginator = Paginator(queryset, 20)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        extra_context = extra_context or {}
        extra_context["form"] = form
        extra_context["products"] = page_obj

        return super().changelist_view(request, extra_context=extra_context)

    # Custom URL patterns to handle CRUD actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/edit/",
                self.admin_site.admin_view(self.edit_product),
                name="edit_product",
            ),
            path(
                "<int:pk>/delete/",
                self.admin_site.admin_view(self.delete_product),
                name="delete_product",
            ),
        ]
        return custom_urls + urls

    # Edit view
    def edit_product(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Product updated successfully.")
                return redirect("admin:yourapp_product_changelist")
        else:
            form = ProductForm(instance=product)

        return render(
            request,
            "admin/product/edit_product.html",
            {"form": form, "product": product},
        )

    # Delete view
    def delete_product(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if request.method == "POST":
            product.delete()
            messages.success(request, "Product deleted successfully.")
            return redirect("admin:yourapp_product_changelist")

        return render(
            request, "admin/product/confirm_delete.html", {"product": product}
        )


class CartAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "get_price_tag", "cart_id"]

    class Meta:
        Model = Cart


class make_accept_refund(
    admin.ModelAdmin,
):
    autocomplete_fields = ["is_refund_request", "refund_granted"]


make_accept_refund.short_description = "update refund granted"


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "items",
        "date",
        "item_price_display",
        "delivery_fee_display",
        "total_price_display",
        "reference",
        "is_ordered",
        "is_delivered",
        "is_received",
        "is_refund_request",
        "refund_granted",
        "view_invoice_button",
        "download_invoice_button",
        "send_invoice_button",
        "approve_order_button",
        "cancel_order_button",
    ]
    # list_filter = [DateListFilter]

    search_fields = ["reference", "product__product__title"]

    # change_list_template = 'admin/orders/orders_filter_template.html'
    # change_list_template = 'admins/orders/order_change_list.html'
    list_per_page = 20
    list_max_show_all = 100
    # Replace with fields you want to be editable
    sortable_by = ["is_ordered"]  # Replace with sortable fields
    search_help_text = "Search help text here."

    def view_invoice(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            invoice = get_object_or_404(Invoice, order=order)
            context = {
                "order": order,
                "invoice": invoice,
                "items": order.product.all(),  # Assuming items is a related name or reverse relation to the order
            }
            return render(request, "store/invoice_template.html", context)
        except Order.DoesNotExist:
            self.message_user(request, "Order does not exist.", level=messages.ERROR)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def send_invoice(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("order_id")
            order = Order.objects.get(id=order_id)
            invoice = get_object_or_404(Invoice, order=order)
            subject = f"Invoice for Order {order.reference}"

            try:
                message = render_to_string(
                    "store/send_invoice.html", {"order": order, "invoice": invoice}
                )
            except TemplateDoesNotExist:
                messages.error(request, "Invoice template not found.")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            email = EmailMessage(subject, message, to=[order.user.email])
            email.content_subtype = "html"
            email.send()

            messages.success(
                request, f"Invoice for order {order.reference} sent successfully."
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        except Order.DoesNotExist:
            messages.error(request, "Order does not exist.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        except Exception as e:
            messages.error(request, f"Error sending invoice: {e}")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    # # Download the invoice as a PDF
    def download_invoice(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            invoice = get_object_or_404(Invoice, order=order)
            context = {"order": order, "invoice": invoice}
            html = render_to_string("store/invoice_template.html", context)
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="invoice_{order.reference}.pdf"'
            )
            result = io.BytesIO()
            pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=result)

            if pisa_status.err:
                return HttpResponse("We had some errors <pre>" + html + "</pre>")

            response.write(result.getvalue())
            return response
        except Order.DoesNotExist:
            self.message_user(request, "Order does not exist.", level=messages.ERROR)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def approve_order(self, request, order_id):
        next_url = request.GET.get("next")

        try:
            order = Order.objects.get(id=order_id)
            # Fetch delivery location based on the order (assuming `delivery_location` field exists in the Order model)
            delivery_location = DeliveryLocations.objects.get(
                state=order.delivery_location.state,
                town_name=order.delivery_location.town_name,
            )
            delivery_days = delivery_location.delivery_days

            # Update order status to approved
            order.approved = True
            order.cancelled = False
            order.save()

            # Send email to user
            subject = f"Order Approved - Reference {order.reference}"
            message = render_to_string(
                "emails/order_approved_email.html",
                {
                    "order": order,
                    "delivery_days": delivery_days,
                },
            )
            email = EmailMessage(subject, message, to=[order.user.email])
            email.content_subtype = "html"
            email.send()

            # Admin feedback message
            # self.message_user(request, f"Order {order.reference} approved successfully and email sent to user.")
            # return redirect(request.GET.get('next', 'admin:view_filtered_orders'))
            messages.success(
                request, f"Invoice for order {order.reference} sent successfully."
            )
            return render(
                request,
                "admins/orders/success_page.html",
                {
                    "message": f"Invoice for order {order.reference} sent successfully.",
                    "next_url": reverse("admin:view_filtered_orders"),
                },
            )

            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Order.DoesNotExist:
            self.message_user(request, "Order does not exist.", level=messages.ERROR)
            return redirect(request.GET.get("next", "admin:view_filtered_orders"))
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except DeliveryLocations.DoesNotExist:
            self.message_user(
                request,
                "Delivery location not found for the order.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        except Exception as e:
            self.message_user(
                request, f"Error approving order: {e}", level=messages.ERROR
            )
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def cancel_order(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if order.approved:
                self.message_user(
                    request, "Cannot cancel an approved order.", level=messages.ERROR
                )
            else:
                # Cancel the order
                order.cancelled = True  # Or set a `canceled` field if it exists
                order.save()

                # Send email notification to the user
                subject = f"Order Canceled - Reference {order.reference}"
                message = render_to_string(
                    "emails/cancel_order_email.html",
                    {
                        "order": order,
                    },
                )
                email = EmailMessage(subject, message, to=[order.user.email])
                email.content_subtype = "html"
                email.send()

                self.message_user(
                    request,
                    f"Order {order.reference} canceled and email sent to the user.",
                )
        except Order.DoesNotExist:
            self.message_user(request, "Order does not exist.", level=messages.ERROR)

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def changelist_view(self, request, extra_context=None):
        # Fetch the original queryset
        queryset = self.get_queryset(request)

        # Get today's date (with timezone awareness if necessary)
        today = make_aware(
            datetime.today()
        )  # Assuming you use timezone-aware DateTimeField

        # Filter queryset by today's date (ignoring time)
        queryset = queryset.filter(date__date=today.date())

        # Filter the queryset for revenue calculations
        total_order_revenue = queryset.filter(is_ordered=True, deleted=False)

        # Calculate total revenue
        total_revenue = sum(
            order.get_total_with_delivery() for order in total_order_revenue
        )

        # Get sales data for chart and pagination
        sales_data = queryset.filter(is_ordered=True, deleted=False, cancelled=False)

        # Extract the dates and quantities into separate lists for the chart

        # Paginate the sales_data (for chart or other displayed data)
        paginator = Paginator(sales_data, 20)  # Show 10 sales per page
        page_number = (
            request.GET.get("page") or 1
        )  # Default to page 1 if no page is specified
        page_obj = paginator.get_page(page_number)

        extra_context = extra_context or {}

        # Order counts and status-based filtering
        extra_context["total_orders"] = queryset.filter(is_ordered=True).count()
        extra_context["count"] = queryset.count()  # Total orders filtered for today
        extra_context["pending_orders"] = queryset.filter(is_ordered=False).count()
        extra_context["user_cancelled"] = queryset.filter(user_cancelled=True).count()
        extra_context["delivered_orders"] = queryset.filter(
            is_delivered=True, is_ordered=True, is_received=True
        ).count()
        extra_context["undelivered_orders"] = queryset.filter(
            is_delivered=False, is_ordered=True, is_received=False
        ).count()
        extra_context["total_revenue"] = total_revenue
        extra_context["sales_dates"] = dates
        extra_context["page_obj"] = page_obj

        # Data for charts
        labels = [
            "Total Orders",
            "Pending Orders",
            "Delivered Orders",
            "Undelivered Orders",
        ]
        values = [
            extra_context["total_orders"],
            extra_context["pending_orders"],
            extra_context["delivered_orders"],
            extra_context["undelivered_orders"],
        ]

        extra_context["chart_labels"] = labels
        extra_context["chart_values"] = values

        # Call the superclass changelist_view
        response = super().changelist_view(request, extra_context=extra_context)

        return response

    def view_filtered_orders(self, request):
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")
        search_query = request.POST.get("search", "")
        queryset = Order.objects.all()

        if request.method == "POST":
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
                    queryset = queryset.filter(date__gte=start_date)
                except ValueError:
                    self.message_user(
                        request, "Invalid start date format.", level=messages.ERROR
                    )
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
                    queryset = queryset.filter(date__lte=end_date)
                except ValueError:
                    self.message_user(
                        request, "Invalid end date format.", level=messages.ERROR
                    )
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            if search_query:
                queryset = queryset.filter(
                    Q(product__product__title__icontains=search_query)
                    | Q(user__username__icontains=search_query)
                    | Q(reference__icontains=search_query)
                )
                search_value = search_query
            else:
                search_value = ""

            try:
                total_order_revenue = queryset.filter(is_ordered=True, deleted=False)
                total_revenue = sum(
                    order.get_total_with_delivery() for order in total_order_revenue
                )

                total_orders = queryset.filter(is_ordered=True).count()
                pending_orders = queryset.filter(is_ordered=False).count()
                delivered_orders = queryset.filter(
                    is_delivered=True, is_ordered=True, is_received=True
                ).count()
                undelivered_orders = queryset.filter(
                    is_delivered=False, is_ordered=True, is_received=False
                ).count()

                # Data for charts
                labels = [
                    "Total Orders",
                    "Pending Orders",
                    "Delivered Orders",
                    "Undelivered Orders",
                ]
                values = [
                    total_orders,
                    pending_orders,
                    delivered_orders,
                    undelivered_orders,
                ]

                paginator = Paginator(queryset, 20)  # Show 10 sales per page
                page_number = (
                    request.GET.get("page") or 1
                )  # Default to page 1 if no page is specified
                page_obj = paginator.get_page(page_number)

                context = {
                    "today": datetime.today(),
                    "count": queryset.count(),
                    "search_value": search_value,
                    "orders": queryset,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "total_orders": total_orders,
                    "pending_orders": pending_orders,
                    "delivered_orders": delivered_orders,
                    "undelivered_orders": undelivered_orders,
                    "total_revenue": total_revenue,
                    "labels": labels,  # Pass labels to the template
                    "values": values,  # Pass values to the template
                    "page_obj": page_obj,
                }
                return render(
                    request, "admins/orders/orders_filter_template.html", context
                )

            except Order.DoesNotExist:
                self.message_user(
                    request, "Order does not exist.", level=messages.ERROR
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    @admin.display(description="Total Price with Delivery")
    def total_price_display(self, obj):
        total_price_value = (
            obj.get_total_with_delivery()
        )  # Call the model method to get the total price with delivery
        formatted_price = "₦{:,.2f}".format(
            float(total_price_value)
        )  # Format the price with a currency symbol
        return formatted_price

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Filter orders to show only those created today by default
        today = now().date()
        return queryset.filter(date__date=today)

    # Display Item(s) Price in a readable format
    @admin.display(description="Item(s) Price")
    def item_price_display(self, obj):
        total_price_value = obj.get_total()
        formatted_price = "₦{:,.2f}".format(float(total_price_value))
        return format_html('<p class="h5">{}</p>', formatted_price)

    # Display Delivery Fee in a readable format
    @admin.display(description="Delivery Fee")
    def delivery_fee_display(self, obj):
        delivery_cost_value = obj.get_delivery_cost()
        formatted_price = "₦{:,.2f}".format(float(delivery_cost_value))
        return format_html('<p class="h5">{}</p>', formatted_price)

    # Display Total Price in a readable format
    @admin.display(description="Total")
    def total_price_display(self, obj):
        total_price_value = obj.get_total_with_delivery()
        formatted_price = "₦{:,.2f}".format(float(total_price_value))
        return format_html('<p class="h5">{}</p>', formatted_price)

    # Custom buttons for viewing, downloading, and sending invoices
    @admin.display(description="Invoice Action")
    def view_invoice_button(self, obj):
        return format_html(
            '<a class="btn btn-light" href="{}">View Invoice</a>',
            reverse("admin:view_invoice", args=[obj.id]),
        )

    @admin.display(description="Download Invoice")
    def download_invoice_button(self, obj):
        return format_html(
            '<a class="btn btn-light" href="{}">Download Invoice</a>',
            reverse("admin:download_invoice", args=[obj.id]),
        )

    @admin.display(description="Send Invoice")
    def send_invoice_button(self, obj):
        return format_html(
            '<a class="btn btn-secondary" href="{}">Send Invoice</a>',
            reverse("admin:send_invoice", args=[obj.id]),
        )

    # Custom buttons for approving and canceling orders
    @admin.display(description="Cancel Order")
    def cancel_order_button(self, obj):
        if not obj.approved:
            return format_html(
                '<a class="btn btn-danger" href="{}">Cancel Order</a>',
                reverse("admin:cancel_order", args=[obj.id]),
            )
        return ""

    @admin.display(description="Approve Order")
    def approve_order_button(self, obj):
        if not obj.approved:
            return format_html(
                '<a class="btn btn-success" href="{}">Approve Order</a>',
                reverse("admin:approve_order", args=[obj.id]),
            )
        return format_html('<button class="btn btn-success">Approved</button>')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:order_id>/view-invoice/",
                self.admin_site.admin_view(self.view_invoice),
                name="view_invoice",
            ),
            path(
                "<int:order_id>send/invoice/",
                self.admin_site.admin_view(self.send_invoice),
                name="send_invoice",
            ),
            path(
                "<int:order_id>/download-invoice/",
                self.admin_site.admin_view(self.download_invoice),
                name="download_invoice",
            ),
            path(
                "<int:order_id>/cancel-order/",
                self.admin_site.admin_view(self.cancel_order),
                name="cancel_order",
            ),
            path(
                "<int:order_id>/approve-order/",
                self.admin_site.admin_view(self.approve_order),
                name="approve_order",
            ),
            path(
                "filter/order-date/",
                self.admin_site.admin_view(self.changelist_view),
                name="filter_order",
            ),
            path(
                "view/filtered_orders/",
                self.admin_site.admin_view(self.view_filtered_orders),
                name="view_filtered_orders",
            ),
        ]
        return custom_urls + urls

    # Add existing invoice view, send, download, approve, and cancel functionality (same as before)
    # ...
    def view_order_report(self, obj):
        return format_html(
            '<a class="button" href="{}">View Report</a>', "/admin/orders/report/"
        )

    view_order_report.short_description = "Order Report"
    view_order_report.allow_tags = True


admin.site.register(Order, OrderAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" style="max-width:50px; max-height:100px"/>'.format(
                obj.img.url
            )
        )

    list_display = ["title", "image_tag"]


class AddressAdmin(admin.ModelAdmin):
    list_display = ["__all__"]


class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "valid_from", "valid_to", "active", "user", "is_used"]

    list_filter = ["active", "valid_from", "valid_to"]

    search_fields = ["code"]


class InventAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity"]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "street_address",
        "apartment",
        "town",
        "state",
        "zip_code",
        "telephone",
    ]


# admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
# admin.site.register(Category, CategoryAdmin)

admin.site.register(CustomersAddress, AddressAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Refunds)
admin.site.register(Color)
admin.site.register(ProductSizeColor)

admin.site.register(Inventory, InventAdmin)

admin.site.register(Size)
admin.site.register(Stock)
admin.site.register(Invoice)

admin.site.register(Wishlist)
actions = [make_accept_refund]

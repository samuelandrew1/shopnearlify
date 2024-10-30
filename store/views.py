import json
import requests
import secrets
import uuid
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from delivery.deliveryform import AddressForm, VerifyPhoneForm
from delivery.models import DeliveryLocations
from .models import *
from django.views.generic import DetailView, ListView, View
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from allauth.account.forms import LoginForm, SignupForm
from django.core.exceptions import ObjectDoesNotExist
from .form import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# from django.conf import settings
from shopnearlify import settings
from django.http import HttpResponse, HttpResponseRedirect

import random
import string
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

# apps.py
from django.db import transaction
from django.apps import AppConfig
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Avg, Count
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC, EmailConfirmation
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404

from .models import EmailSubscription
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import render_to_string

from django.utils.html import strip_tags


class StoreConfig(AppConfig):
    name = "book_store"

    def ready(self):
        import book_store.signals

        print("Signals imported and ready.")


# class CustomConfirmEmailView(ConfirmEmailView):
#     template_name = "account/custom_email_confirm.html"  # Specify the custom template

#     def get_object(self, queryset=None):
#         """ Retrieve the confirmation object using either EmailConfirmation or EmailConfirmationHMAC """
#         key = self.kwargs['key']
#         try:
#             # Try to retrieve confirmation using HMAC
#             obj = EmailConfirmationHMAC.from_key(key)
#             if obj:
#                 return obj
#             # If not found, use EmailConfirmation model
#             obj = EmailConfirmation.objects.get(key=key.lower())
#             return obj
#         except EmailConfirmation.DoesNotExist:
#             raise Http404("Email confirmation link expired or invalid.")

#     def get(self, request, *args, **kwargs):
#         try:
#             confirmation = self.get_object()
#             confirmation.confirm(request)  # Confirm and verify the email
#             # Redirect to login or a success page
#             return redirect(reverse('account_login'))  # Replace with your desired URL
#         except Http404:
#             # Redirect to an appropriate page if the link is invalid or expired
#             return redirect(reverse('account_email_verification_sent'))


# get or create session key
def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


class DashBoardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile_form = UserProfileForm(instance=self.request.user)
        password_form = PasswordChangeForm(self.request.user)
        cart = Cart.objects.filter(user=self.request.user, is_ordered=True)
        orders = Order.objects.filter(user=self.request.user, is_ordered=True).order_by(
            "id"
        )
        address = CustomersAddress.objects.filter(user=self.request.user).first()
        address_form = AddressForm(instance=address)

        # # Fetch all products the user has reviewed
        # reviewed_products = Rating.objects.filter(user_ratings=self.request.user).values_list('object_id', flat=True)

        # # Fetch all products in the user's orders that have not been reviewed yet
        # unreviewed_products = Product.objects.filter(order__in=orders).exclude(id__in=reviewed_products).distinct()

        context = {
            "profile_form": profile_form,
            "password_form": password_form,
            "orders": orders,
            "cart": cart,
            "address": address,
            "address_form": address_form,
            # 'rating_form': CustomerRatingForm(),
            # 'unreviewed_products': unreviewed_products,  # Pass unreviewed products to context
        }
        return render(self.request, "store/dashboard.html", context)

    def post(self, request, *args, **kwargs):
        profile_form = UserProfileForm(self.request.POST, instance=self.request.user)
        password_form = PasswordChangeForm(self.request.user, self.request.POST)
        address = CustomersAddress.objects.filter(user=self.request.user).first()
        address_form = (
            AddressForm(self.request.POST, instance=address)
            if address
            else AddressForm(self.request.POST)
        )

        if "update_profile" in self.request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(
                self.request, "Your profile has been updated successfully!"
            )
            return redirect("store:dash-board")

        elif "change_password" in self.request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)  # Important!
            messages.success(
                self.request, "Your password has been changed successfully!"
            )
            return redirect("store:dash-board")

        elif "update_address" in self.request.POST and address_form.is_valid():
            address_form.save(commit=False)
            address_form.instance.user = (
                self.request.user
            )  # Ensure the address is linked to the current user
            address_form.save()
            messages.success(
                self.request, "Your address has been updated successfully!"
            )
            return redirect("store:dash-board")
        else:
            messages.error(
                request,
                "There was an error with your submission. Please correct the errors below.",
            )
            return redirect("store:dash-board")

        # Fetch all products the user has reviewed
        reviewed_products = Rating.objects.filter(
            user_ratings=self.request.user
        ).values_list("object_id", flat=True)

        # # Fetch all products in the user's orders that have not been reviewed yet
        unreviewed_products = (
            Product.objects.filter(
                order__in=Order.objects.filter(user=self.request.user, is_ordered=True)
            )
            .exclude(id__in=reviewed_products)
            .distinct()
        )

        context = {
            "profile_form": profile_form,
            "password_form": password_form,
            "orders": Order.objects.filter(
                user=self.request.user, is_ordered=True
            ).order_by("id"),
            "cart": Cart.objects.filter(user=self.request.user, is_ordered=True),
            "address": address,
            "address_form": address_form,
            "rating_form": CustomerRatingForm(),
            "unreviewed_products": unreviewed_products,  # Pass unreviewed products to context
        }
        return render(self.request, "store/dashboard.html", context)


def rate_product(request, slug):
    form = CustomerRatingForm(request.POST or None)
    product = get_object_or_404(Product, slug=slug)
    context = {"form": form, "product": product}
    return render(request, "store/rate_product.html", context)


def generate_random_number(digits=10):
    if digits > 10:
        raise ValueError("The number of digit sshould not exceed 10")
    if digits < 1:
        raise ValueError("The number of digits should be at least 1")

    lower_bound = 10 ** (digits - 1)
    upper_bound = 10**digits - 1

    return random.randint(lower_bound, upper_bound)


def create_ref_code():  # generate order reference code
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=15))


def contact_view(request):
    return render(request, "store/contact.html")


# display all the category of product
def ProductCategories_view(request):
    if request.method == "GET":
        # Get filter parameters from the request
        category_filter = request.GET.get("category")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        size_filter = request.GET.get("size")
        description_filter = request.GET.get("description")

        # Get all products and apply filters
        # products = Product.objects.select_related('category').all().order_by('id')  # Order the QuerySet by 'id'
        products = (
            Product.objects.select_related("category")
            .prefetch_related("size", "ratings")
            .all()
            .order_by("id")
        )

        if category_filter:
            products = products.filter(category__id=category_filter)
        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        if size_filter:
            products = products.filter(size=size_filter)

        if description_filter:
            products = products.filter(description__icontains=description_filter)

        # Get all categories for the filter menu
        categories = Category.objects.all().order_by("title")

        # Implement pagination
        paginator = Paginator(products, 20)  # Show 20 products per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        products_with_ratings = []
        for product in page_obj:
            sizes = product.size.all()
            total_stock = (
                Stock.objects.filter(product=product).aggregate(Sum("quantity"))[
                    "quantity__sum"
                ]
                or 0
            )
            avg_rating = product.average_rating()
            count = product.ratings.count()
            products_with_ratings.append(
                {
                    "product": product,
                    "total_stock": total_stock,
                    "sizes": sizes,
                    "average_rating": avg_rating,
                    "count": count,
                }
            )

        context = {
            "category": categories,
            "products_with_ratings": products_with_ratings,
            "page_obj": page_obj,
            "selected_category": category_filter,
            "min_price": min_price,
            "max_price": max_price,
            "selected_size": size_filter,
            "description_filter": description_filter,
        }
        return render(request, "store/category.html", context)


def product_list_by_category(request, slug):
    try:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category).order_by(
            "id"
        )  # Order the QuerySet by 'id'
        sizes = Size.objects.all().distinct()  # Get unique sizes

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        size_id = request.GET.get("size")

        if min_price and max_price:
            # Filter products based on size prices within the range
            products = products.filter(
                product__size__discount_price__gte=min_price,
                product__size__discount_price__lte=max_price,
            )

        if size_id:
            products = products.filter(size__size=size_id)

        products_with_ratings = [
            {"product": product, "average_rating": product.average_rating()}
            for product in products
        ]

        # Pagination
        page = request.GET.get("page", 1)
        paginator = Paginator(products_with_ratings, 10)  # Show 10 products per page

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        context = {
            "category": category,
            "products": products,
            "products_with_ratings": paginated_products,
            "min_price": min_price,
            "max_price": max_price,
            "size_id": size_id,
            "sizes": sizes,
            "product_count": products.count(),
        }
        return render(request, "store/product_list_by_category.html", context)
    except ObjectDoesNotExist:
        messages.error(request, "not found on the server")
        return redirect("store:index")


def logout_view(request):

    logout(request)
    return redirect("store/index.html")


def register(request):
    form = SignupForm()
    return render(request, "account/signup.html", {"form": form})


def login(request):

    form = LoginForm()
    return render(request, "account/login.html", {"form": form})


def home_view(request):
    top_products = Product.objects.get_top_products()
    featured_products = Product.get_featured_products()
    top_rated_products = Product.get_top_rated_products()
    products_on_sale = Product.get_products_on_sale()
    get_deal_of_the_day_products = Product.get_deal_of_the_day_products()
    categories = Category.objects.all()  # fetch all the category of products
    category_products = {}
    # top_selling_by_category = Product.objects.get_top_selling_by_category()
    new_products = Product.objects.get_new_products()
    categories = Category.objects.all()
    top_selling_by_category = Product.get_top_selling_by_category()

    # top_discounted_products = Product.objects.get_top_discounted_products()
    context = {
        "top_products": top_products,
        "featured_products": featured_products,
        "top_rated_products": top_rated_products,
        "products_on_sale": products_on_sale,
        "deal_of_the_day": get_deal_of_the_day_products,
        "category_products": category_products,
        "categories": categories,
        "top_selling_by_category": top_selling_by_category,
        "new_products": new_products,
        # 'top_discounted_products': top_discounted_products,
    }
    return render(request, "store/index.html", context)


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


logger = logging.getLogger(__name__)


class CartView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        try:
            coupon_form = CouponForm()
            location_form = DeliveryLocations()

            if request.user.is_authenticated:
                cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
                order = Order.objects.filter(
                    user=request.user, is_ordered=False, deleted=False, cancelled=False
                ).first()
            else:
                session_cart_id = request.session.get("cart_id")
                if not session_cart_id:
                    session_cart_id = str(uuid.uuid4())
                    request.session["cart_id"] = session_cart_id

                cart_items = Cart.objects.filter(
                    session_key=session_cart_id, is_ordered=False
                )
                order = Order.objects.filter(
                    session_key=session_cart_id, is_ordered=False
                ).first()
                print("amount", cart_items.count())
            coupons = Coupon.objects.filter(active=True)
            locations = DeliveryLocations.objects.all()

            # Create a dictionary to hold color quantities for each cart item
            color_quantities = {}
            for cart_item in cart_items:
                cart_colors = CartColor.objects.filter(cart=cart_item)
                color_quantities[cart_item.id] = {
                    "slug": cart_item.product.id,
                    "colors": {
                        cart_color.color.name: cart_color.quantity
                        for cart_color in cart_colors
                    },
                }

            context = {
                "coupon_form": coupon_form,
                "location_form": location_form,
                "locations": locations,
                "coupons": coupons,
                "order": order,
                "cart_items": cart_items,
                "color_quantities": color_quantities,
                "total_with_delivery": order.get_total_with_delivery() if order else 0,
                # 'minimum_order':max_value,
            }
            return render(request, "store/cart.html", context)
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order.")
            return redirect("store:categories")

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                order = Order.objects.filter(
                    user=request.user, is_ordered=False
                ).first()
            else:
                session_cart_id = request.session.get("cart_id")
                if not session_cart_id:
                    session_cart_id = str(uuid.uuid4())
                    request.session["cart_id"] = session_cart_id
                    request.session.modified = True

                order = Order.objects.filter(
                    cart_id=session_cart_id, is_ordered=False
                ).first()

            coupon_form = CouponForm(request.POST)
            location_form = DeliveryLocations(request.POST)
            if coupon_form.is_valid():
                coupon_code = coupon_form.cleaned_data["code"]
                try:
                    coupon = Coupon.objects.get(code=coupon_code, active=True)
                    order.coupon = coupon
                    order.save()
                    messages.success(request, "Coupon applied successfully.")
                except Coupon.DoesNotExist:
                    messages.error(request, "Invalid coupon code.")

            # if location_form.is_valid():
            #     location_id = location_form.cleaned_data['location']
            #     abuja_location = AbujaLocation.objects.get(id=location_id)
            #     order.abuja_location = abuja_location
            #     order.save()
            #     messages.success(request, 'Delivery location updated successfully.')

            if request.user.is_authenticated:
                cart_items = Cart.objects.filter(
                    user=request.user, is_ordered=False, cancelled=False
                )
            else:
                cart_items = Cart.objects.filter(
                    cart_id=session_cart_id, is_ordered=False, cancelled=False
                )

            # Create a dictionary to hold color quantities for each cart item
            color_quantities = {}
            for cart_item in cart_items:
                cart_colors = CartColor.objects.filter(cart=cart_item)
                color_quantities[cart_item.id] = {
                    "product_id": cart_item.product.id,
                    "colors": {
                        cart_color.color.name: cart_color.quantity
                        for cart_color in cart_colors
                    },
                }

            coupons = Coupon.objects.filter(active=True)
            locations = DeliveryLocations.objects.all()
            context = {
                "coupon_form": coupon_form,
                "location_form": location_form,
                "locations": locations,
                "coupons": coupons,
                "order": order,
                "cart_items": cart_items,
                "total_with_delivery": order.get_total_with_delivery() if order else 0,
                "color_quantities": color_quantities,
            }

            return render(request, "store/cart.html", context)

        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order.")
            return redirect("store:cart")

    def put(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            cart_id = int(request.POST.get("cart_id"))
            quantity_data = request.POST.getlist("quantities[]")
            color_data = request.POST.getlist("colors[]")

            quantities = []
            for qty in quantity_data:
                try:
                    quantities.append(int(qty))
                except (ValueError, TypeError):
                    return JsonResponse({"message": "Invalid quantity"}, status=400)

            cart_item = get_object_or_404(Cart, pk=cart_id)

            if request.user.is_authenticated:
                cart_item.quantity = sum(quantities)

                CartColor.objects.filter(cart=cart_item).delete()
                for color_name, qty in zip(color_data, quantities):
                    if qty > 0:
                        color = get_object_or_404(Color, name=color_name)
                        CartColor.objects.create(
                            cart=cart_item, color=color, quantity=qty
                        )

                cart_item.save()
            else:
                session_cart = request.session.get("cart", {})
                if str(cart_id) in session_cart:
                    session_cart[str(cart_id)]["quantity"] = sum(quantities)
                    session_cart[str(cart_id)]["colors"] = [
                        {"color": color, "quantity": qty}
                        for color, qty in zip(color_data, quantities)
                        if qty > 0
                    ]
                else:
                    session_cart[str(cart_id)] = {
                        "quantity": sum(quantities),
                        "colors": [
                            {"color": color, "quantity": qty}
                            for color, qty in zip(color_data, quantities)
                            if qty > 0
                        ],
                    }

                request.session["cart"] = session_cart

            total_price = (
                cart_item.product.discount_price * sum(quantities)
                if cart_item.product.discount_price
                else cart_item.product.price * sum(quantities)
            )

            return JsonResponse(
                {
                    "product": cart_item.product.title,
                    "id": cart_id,
                    "qty": sum(quantities),
                    "total_price": total_price,
                    "message": "Cart updated successfully",
                }
            )

        return JsonResponse({"message": "error"}, status=400)


def cart_count_view(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user, is_ordered=False).count()
    else:
        session_cart_id = request.session.get("cart_id", None)
        if session_cart_id:
            cart_count = Cart.objects.filter(
                session_key=session_cart_id, is_ordered=False
            ).count()
        else:
            cart_count = 0
    return JsonResponse({"cart_count": cart_count})


logger = logging.getLogger(__name__)


@csrf_exempt
def delete_cart(request):
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        cart_item_id = request.POST.get("cart_item_id")
        if cart_item_id:
            cart_item = get_object_or_404(Cart, id=cart_item_id, is_ordered=False)
            cart_item.delete()
            # messages.success(request, 'Deleted from cart')
            if request.user.is_authenticated:
                cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
            else:
                session_cart_id = request.session.get("cart_id")
                if session_cart_id:
                    cart_items = Cart.objects.filter(
                        cart_id=session_cart_id, is_ordered=False
                    )
                else:
                    return JsonResponse(
                        {"message": "No active cart found in session"}, status=400
                    )
            cart_total = sum(
                (
                    (
                        item.size.discount_price * item.quantity
                        if item.quantity < item.product.minimum_order
                        else item.size.wholesale_price * item.quantity
                    )
                    if item.size
                    else 0
                )
                for item in cart_items
            )
            # cart_total = sum(item.product.size.discount_price * item.quantity if item.quantity < item.product.minimum_order else item.product.wholesale_price * item.quantity for item in cart_items)
            return JsonResponse({"success": True, "cart_total": cart_total})
        return JsonResponse({"message": "Cart item ID not provided"}, status=400)
    return JsonResponse({"message": "Invalid request"}, status=400)


# @login_required
# def verify_address_and_pay(request):
#     # Fetch user's addresses
#     user_addresses = CustomersAddress.objects.filter(user=request.user)

#     # Fetch current order details
#     orders = Order.objects.filter(user=request.user, is_ordered=False)

#     total_order_cost = 0
#     total_delivery_cost = 0
#     total_cost_with_delivery = 0
#     order = None
#     order_items = []
#     coupon = None

#     if orders.exists():
#         order = orders.first()
#         total_order_cost = order.get_total()  # Assuming get_total() method calculates total cost
#         total_delivery_cost = order.get_delivery_cost()  # Assuming get_delivery_cost() method calculates delivery cost
#         total_cost_with_delivery = total_order_cost + total_delivery_cost
#         order_items = order.product.all()  # Access the related products directly from the order
#         if order.coupon:
#             coupon = order.coupon
#     context = {

#         'addresses': user_addresses,
#         'order': order,
#         'total_order_cost': total_order_cost,
#         'total_delivery_cost': total_delivery_cost,
#         'total_cost_with_delivery': total_cost_with_delivery,
#         'order_items': order_items,
#         'coupon': [coupon] if coupon else None,
#         # 'payment': payment if payment else None
#     }
#     if request.method == 'POST':
#         amount = request.POST['amount']
#         email = request.POST['email']
#         pk = settings.PAYSTACK_PUBLIC_KEY

#     # Convert amount to float instead of int
#         payment = Payment.objects.create(amount=float(amount), email=email, order=order, user=request.user)
#         payment.save()
#         context = {

#         'addresses': user_addresses,
#         'order': order,
#         'total_order_cost': total_order_cost,
#         'total_delivery_cost': total_delivery_cost,
#         'total_cost_with_delivery': total_cost_with_delivery,
#         'order_items': order_items,
#         'coupon': [coupon] if coupon else None,
#         'payment':payment
#     }

#         return render('store:check-user-address.html')

#     return render(request, 'store/check-user-address.html', context)


def load_cities(request):
    state = request.GET.get("state")  # Get state from the AJAX request
    cities = DeliveryLocations.objects.filter(state=state).values(
        "town_name"
    )  # Query cities based on state
    return JsonResponse(
        list(cities), safe=False
    )  # Return as JSON  return JsonResponse(list(cities), safe=False)


# @method_decorator(login_required, name='dispatch')
# class CheckoutView(View):
#     def get(self, *args, **kwargs):

#         profile, created = Profile.objects.get_or_create(user=self.request.user)
#         # if not profile.phone_number or not profile.is_phone_verified:
#         #     messages.warning(self.request, "Please provide your phone number before proceeding to checkout.")
#         #     return redirect('delivery:phone_number_verify')
#         # # Check if the user has an existing address
#         try:
#             address = CustomersAddress.objects.get(user=self.request.user)
#             form = AddressForm(instance=address)  # Pre-populate form with the existing address
#         except CustomersAddress.DoesNotExist:
#             form = AddressForm()  # If no existing address, present a blank form

#         coupon = Coupon.objects.filter(active=True)
#         states = DeliveryLocations.objects.all()

#         try:
#             order = Order.objects.get(user=self.request.user, is_ordered=False)
#             cart = Cart.objects.filter(user=self.request.user, is_ordered=False)

#             if not cart.exists():
#                 messages.warning(self.request, 'Your cart is empty.')
#                 return redirect('store:cart')

#             # Pre-populate the phone number in the form if it's verified
#             form.fields['telephone'].initial = profile.phone_number

#             context = {
#                 'coupon': coupon,
#                 'states': states,
#                 'form': form,
#                 'order': order,
#                 'cart': cart,
#                 'coupon_form': CouponForm(),
#             }

#             return render(self.request, 'store/checkout.html', context)

#         except Order.DoesNotExist:
#             messages.error(self.request, 'You do not have an active order')
#             return redirect('store:categories-list')

#     def post(self, *args, **kwargs):
#         try:
#             form = AddressForm(self.request.POST or None)
#             order = Order.objects.get(user=self.request.user, is_ordered=False)

#             if form.is_valid():
#                 street_address = form.cleaned_data.get('street_address')
#                 apartment = form.cleaned_data.get('apartment')
#                 town = form.cleaned_data.get('town')
#                 state = form.cleaned_data.get('state')
#                 country = form.cleaned_data.get('country')
#                 zip_code = form.cleaned_data.get('zip_code')

#                 # Get delivery cost based on state and town
#                 delivery_location = get_object_or_404(DeliveryLocations, state=state, town_name=town)

#                 # Check if the user already has an address
#                 address, created = CustomersAddress.objects.update_or_create(
#                     user=self.request.user,
#                     defaults={
#                         'street_address': street_address,
#                         'apartment': apartment,
#                         'town': town,
#                         'state': state,
#                         'country': country,
#                         'zip_code': zip_code,
#                     }
#                 )

#                 # Update the order with the new shipping address and delivery location
#                 order.shipping_address = address
#                 order.delivery_location = delivery_location  # Set delivery location
#                 order.save()  # Save the order with the updated delivery location

#                 # Calculate the total with delivery
#                 total_with_delivery = order.get_total_with_delivery()  # Use the method to calculate total
#                 order.total_price = total_with_delivery  # Update the order total price
#                 order.save()  # Save again after updating the total price with delivery

#                 return redirect('paystack:initiate_payment')

#             messages.warning(self.request, 'Order failed')
#             return redirect('store:cart')

#         except ObjectDoesNotExist:
#             messages.error(self.request, 'You do not have an active order')
#             return redirect('store:categories')


@method_decorator(login_required, name="dispatch")
class CheckoutView(View):
    def get(self, *args, **kwargs):
        # Get or create the user's profile
        profile = Profile.objects.filter(user=self.request.user).first()
        if not profile:
            profile = Profile.objects.create(user=self.request.user)

        try:
            address = CustomersAddress.objects.get(user=self.request.user)
            form = AddressForm(
                instance=address
            )  # Pre-populate form with the existing address
        except CustomersAddress.DoesNotExist:
            form = AddressForm()  # If no existing address, present a blank form

        coupon = Coupon.objects.filter(active=True)
        states = DeliveryLocations.objects.all()

        try:
            order = Order.objects.get(
                user=self.request.user, is_ordered=False, cancelled=False
            )
            cart = Cart.objects.filter(
                user=self.request.user, is_ordered=False, cancelled=False
            )

            if not cart.exists():
                messages.warning(self.request, "Your cart is empty.")
                return redirect("store:cart")

            # Pre-populate the phone number in the form if it's verified
            form.fields["telephone"].initial = profile.phone_number

            context = {
                "coupon": coupon,
                "states": states,
                "form": form,
                "order": order,
                "cart": cart,
                "coupon_form": CouponForm(),
            }

            return render(self.request, "store/checkout.html", context)

        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("store:categories-list")

    def post(self, *args, **kwargs):
        form = AddressForm(self.request.POST or None)

        try:
            order = Order.objects.get(
                user=self.request.user, is_ordered=False, cancelled=False
            )
        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("store:categories-list")

        if form.is_valid():
            street_address = form.cleaned_data.get("street_address")
            apartment = form.cleaned_data.get("apartment")
            town = form.cleaned_data.get("town")
            state = form.cleaned_data.get("state")
            country = form.cleaned_data.get("country")
            zip_code = form.cleaned_data.get("zip_code")
            telephone = form.cleaned_data.get("telephone")

            try:
                # Get delivery cost based on state and town
                delivery_location = DeliveryLocations.objects.get(
                    state=state, town_name=town
                )
            except DeliveryLocations.DoesNotExist:
                messages.error(
                    self.request,
                    "Delivery location not found for the selected state and town.",
                )
                return render(self.request, "store/checkout.html", {"form": form})

            # Check if the user already has an address
            address, created = CustomersAddress.objects.update_or_create(
                user=self.request.user,
                defaults={
                    "street_address": street_address,
                    "apartment": apartment,
                    "town": town,
                    "state": state,
                    "country": country,
                    "zip_code": zip_code,
                    "telephone": telephone,
                },
            )

            # Update or get the user's profile (do not create a new one if it exists)
            profile = Profile.objects.filter(user=self.request.user).first()
            if profile:
                profile.phone_number = telephone
                profile.country = country
                profile.save()

            # Update the order with the new shipping address and delivery location
            order.shipping_address = address
            order.delivery_location = delivery_location  # Set delivery location
            order.save()  # Save the order with the updated delivery location

            # Calculate the total with delivery
            total_with_delivery = (
                order.get_total_with_delivery()
            )  # Use the method to calculate total
            order.total_price = total_with_delivery  # Update the order total price
            order.save()  # Save again after updating the total price with delivery

            return redirect("paystack:initiate_payment")

        # Form is not valid, render the form with error messages
        messages.warning(self.request, "Please correct the errors below.")
        print(form.errors)
        return render(
            self.request,
            "store/checkout.html",
            {
                "form": form,
                "order": order,
                "states": DeliveryLocations.objects.all(),
                "coupon": Coupon.objects.filter(active=True),
                "coupon_form": CouponForm(),
            },
        )


# next_url = request.GET.get('next')  # Define next_url early in the code


def Update_addressView(request, pk):
    next_url = request.GET.get("next")  # Define next_url early in the code

    # Fetch the address using get_object_or_404 to ensure it exists
    address = get_object_or_404(CustomersAddress, user=request.user, pk=pk)
    if request.method == "POST":
        order = Order.objects.get(user=request.user, is_ordered=False, cancelled=False)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(
                commit=False
            )  # Save the form but don't commit yet
            updated_address.user = (
                request.user
            )  # Ensure the address is linked to the user
            updated_address.save()  # Now save the instance
            order.delivery_location = updated_address
            order.save()
            messages.success(request, "Your address has been updated.")
            return redirect("store:verify-address")
    else:
        form = AddressForm(instance=address)

    context = {
        "form": form,
    }
    return render(request, "store/update_address.html", context)


@login_required
def verify_address_and_pay(request):
    # Fetch user's addresses
    user_addresses = CustomersAddress.objects.filter(user=request.user)
    pk = settings.PAYSTACK_PUBLIC_KEY
    # Fetch current order details
    orders = Order.objects.filter(user=request.user, is_ordered=False, cancelled=False)

    total_order_cost = 0
    total_delivery_cost = 0
    total_cost_with_delivery = 0
    order = None
    order_items = []
    coupon = None
    payment = None  # Initialize payment as None

    if orders.exists():
        order = orders.first()
        total_order_cost = order.get_total()  # get_total() method calculates total cost
        total_delivery_cost = (
            order.get_delivery_cost()
        )  # get_delivery_cost() method calculates delivery cost
        total_cost_with_delivery = total_order_cost + total_delivery_cost
        order_items = (
            order.product.all()
        )  # Access the related products directly from the order
        if order.coupon:
            coupon = order.coupon

    if request.method == "POST":
        # Generate a unique reference number
        amount = request.POST["amount"]
        email = request.POST["email"]
        # Create the Payment object immediately
        payment = Payment.objects.create(
            amount=float(amount),  # Store in naira
            email=email,
            order=order,
            user=request.user,
            ref=create_ref_code(),
            verified=False,  # Initially not verified
        )
        payment.save()

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": email,
            "amount": amount,
        }
        url = "https://api.paystack.co/transaction/initialize"

        # Log the data being sent to Paystack
        print(f"Initializing Paystack transaction: {data}")

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()

        if response_data["status"]:
            # Log successful initialization
            print(f"Paystack initialization successful: {response_data}")

            authorization_url = response_data["data"]["authorization_url"]
            return redirect(authorization_url)
        else:
            # Handle error here
            print(f"Error initializing Paystack transaction: {response_data}")
            context = {
                "addresses": user_addresses,
                "order": order,
                "total_order_cost": total_order_cost,
                "total_delivery_cost": total_delivery_cost,
                "total_cost_with_delivery": total_cost_with_delivery,
                "order_items": order_items,
                "coupon": [coupon] if coupon else None,
                "error": "There was a problem initializing the payment. Please try again.",
            }
            return render(request, "store/check-user-address.html", context)

    context = {
        "addresses": user_addresses,
        "order": order,
        "total_order_cost": total_order_cost,
        "total_delivery_cost": total_delivery_cost,
        "total_cost_with_delivery": total_cost_with_delivery,
        "order_items": order_items,
        "coupon": [coupon] if coupon else None,
        "paystack_pub_key": pk,
        "ref": generate_random_number(),
    }
    return render(request, "store/check-user-address.html", context)


def success_page(request):
    return render(request, "store/success.html")


class RequestRefund(View):

    def get(self, *args, **kwargs):
        form = RefundRequestForm()
        context = {"form": form}
        return render(self.request, "store/refundpage.html", context)

    def post(self, *args, **kwargs):
        form = RefundRequestForm(self.request.POST or None)
        if form.is_valid():
            try:
                reference = form.cleaned_data.get("reference_code")
                message = form.cleaned_data.get("message")
                email = form.cleaned_data.get("email")
                order = Order.objects.get(reference=reference)
                order.is_refund_request = True
                order.save()

                refund = Refunds()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.success(self.request, "your request is received")
                return redirect("store:index")
            except ObjectDoesNotExist:
                messages.error(self.request, "invalid order")
                return redirect("store:index")
        messages.error(self.request, "invalid order")
        return redirect("store:index")


def apply_coupon(request):
    next_url = request.GET.get("next")  # Define next_url early in the code

    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get("code")
            try:
                coupon = Coupon.objects.get(code=code, active=True)
                current_time = timezone.now()

                # Check if the coupon is within the validity period
                if coupon.valid_from and coupon.valid_to:
                    if not (coupon.valid_from <= current_time <= coupon.valid_to):
                        messages.warning(request, "This coupon has expired.")
                        if next_url and url_has_allowed_host_and_scheme(
                            next_url, allowed_hosts={request.get_host()}
                        ):
                            return redirect(next_url)
                        return redirect("store:index")

                # Check if the user has already used this coupon
                if coupon.used_by.filter(id=request.user.id).exists():
                    messages.warning(request, "You have already used this coupon.")
                    if next_url and url_has_allowed_host_and_scheme(
                        next_url, allowed_hosts={request.get_host()}
                    ):
                        return redirect(next_url)
                    return redirect("store:index")

                order = get_object_or_404(
                    Order, user=request.user, is_ordered=False, cancelled=False
                )
                order.coupon = coupon
                order.save()

                # Mark the coupon as used by this user
                coupon.used_by.add(request.user)
                coupon.save()

                messages.success(request, "Coupon is applied")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url, allowed_hosts={request.get_host()}
                ):
                    return redirect(next_url)
                return redirect("store:index")

            except Coupon.DoesNotExist:
                messages.warning(request, "This coupon does not exist or is not valid")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url, allowed_hosts={request.get_host()}
                ):
                    return redirect(next_url)
                return redirect("store:index")

    else:
        form = CouponForm()
    return render(request, "store/apply_coupon.html", {"form": form})


class DeliveryUpdate(View):
    def post(self, *args, **kwargs):
        status = self.request.POST.get("confirm")
        order = Order.objects.get(
            user=self.request.user, is_ordered=True, is_received=False, cancelled=False
        )
        if status:
            order.is_received = True
            order.save()
            messages.success(self.request, "updated")
            return redirect("store:dash-board")
        messages.error(self.request, "not updated")
        return redirect("store:dash-board")


def order_summary(request):
    order = get_object_or_404(
        Order, user=request.user, is_ordered=False, cancelled=False
    )
    context = {"order": order, "total": order.get_total()}
    return render(request, "store/order_summary.html", context)


# search view query
def search_view(request):
    query = request.GET.get("q")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    results = Product.objects.all().annotate(num_sizes=Count("size")).distinct()

    if query:
        results = (
            results.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__title__icontains=query)
            )
            .annotate(num_sizes=Count("size"))
            .distinct()
        )

    if min_price:
        try:
            min_price = float(min_price)
            results = (
                results.filter(size__price__gte=min_price)
                .annotate(num_sizes=Count("size"))
                .distinct()
            )
        except ValueError:
            pass

    if max_price:
        try:
            max_price = float(max_price)
            results = (
                results.filter(size__price__lte=max_price)
                .annotate(num_sizes=Count("size"))
                .distinct()
            )
        except ValueError:
            pass

    products_with_sizes = []
    for product in results:
        sizes = product.size.all().distinct()
        ratings = product.average_rating()
        color = product.color.all().distinct()
        products_with_sizes.append(
            {"product": product, "color": color, "ratings": ratings, "sizes": sizes}
        )

    context = {
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
        "products_with_sizes": products_with_sizes,
    }

    return render(request, "store/search_results.html", context)


@transaction.atomic
@ensure_csrf_cookie
def product_detail(request, slug):
    form_slug = request.POST.get("product_slug")
    product = get_object_or_404(Product, slug=slug) if slug else form_slug
    colors = product.color.all()  # Fetch only the colors associated with the product
    sizes = product.size.all()  # Fetch only the sizes associated with the product
    # size_color = ProductSizeColor.objects.filter(product=product).values('size', 'color').distinct()
    size_color = ProductSizeColor.objects.filter(product=product).select_related(
        "size", "color"
    )

    if request.user.is_authenticated:
        in_wishlist = (
            Wishlist.objects.filter(user=request.user, product=product).exists(),
        )
        is_in_cart = Cart.objects.filter(
            product=product, is_ordered=False, user=request.user
        ).exists()
        user_rating = CustomerRating.objects.filter(
            user=request.user, product=product
        ).first()
        cart = Cart.objects.filter(
            product=product, is_ordered=False, user=request.user
        ).first()
        print({"user": request.user.profile.phone_number}, "added to cart ")
    else:
        session_key = get_session_key(request)
        is_in_cart = Cart.objects.filter(
            product=product, is_ordered=False, session_key=session_key
        ).exists()
        in_wishlist = Wishlist.objects.filter(
            session_key=session_key, product=product
        ).exists()
        user_rating = None
        cart = Cart.objects.filter(
            product=product, is_ordered=False, session_key=session_key
        ).first()

    ratings = product.ratings.all()
    average_rating = product.average_rating()
    all_user_rating = (
        product.ratings.filter(user=request.user)
        if request.user.is_authenticated
        else None
    )
    next_product = product.get_next_product()
    related_products = product.get_related_products()

    if request.method == "POST" and request.user.is_authenticated:
        rating_form = CustomerRatingForm(request.POST, instance=user_rating)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()
            messages.success(request, "thank you for reviewing our products")
            return redirect("store:product-detail", slug=product.slug)
    else:
        rating_form = (
            CustomerRatingForm(instance=user_rating)
            if request.user.is_authenticated
            else None
        )

    color_quantities = {}
    if cart:
        for color in colors:
            cart_color = CartColor.objects.filter(cart=cart, color=color).first()
            color_quantities[color.name] = cart_color.quantity if cart_color else 0

    cart_quantity = cart.quantity if is_in_cart and cart else None

    size_discount_percentages = {}
    for size in sizes:
        if size.discount_price and size.price:
            discount_percentage = (
                (size.price - size.discount_price) / size.price
            ) * 100
            size_discount_percentages[size.id] = discount_percentage

    context = {
        "product": product,
        "ratings": ratings,
        "average_rating": average_rating,
        "count": product.ratings.count(),
        # 'rating_form': rating_form,
        "now": timezone.now(),
        "all_user_rating": all_user_rating,
        "is_in_cart": is_in_cart,
        "next_product": next_product,
        "related_products": related_products,
        "in_wishlist": in_wishlist,
        "size_discount_percentages": size_discount_percentages,
        "size_colors": size_color,
    }

    return render(request, "store/product_detail.html", context)


# this function enables users to delete a product from the cart
class DeleteCartItem(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            slug = request.POST.get(
                "slug"
            )  # Ensure to convert the slug to an integer before using it
            product = get_object_or_404(
                Product, slug=slug
            )  # Ensure to get the product using the primary key

            if request.user.is_authenticated:  # Check if the user is authenticated
                cart_item = get_object_or_404(
                    Cart, product=product, is_ordered=False, user=request.user
                )  # Ensure to get the cart item using the product and user
                cart_item.delete()  # Delete the cart item
            else:
                session_cart = request.session.get(
                    "cart", {}
                )  # Get the cart from the session
                if str(slug) in session_cart:  # Check if the product is in the cart
                    del session_cart[str(slug)]  # Delete the product from the cart
                    request.session["cart"] = session_cart  # Update the session cart

            return JsonResponse(
                {
                    "product": product.title,
                    "slug": slug,
                    "button_text": "Add to Cart",
                    "csrf_token": request.META.get("CSRF_COOKIE"),
                }
            )

        return JsonResponse({"message": "error"}, status=400)


def mark_order_as_received(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    next_url = request.GET.get("next")  # Define next_url early in the code
    if request.method == "POST":
        order.is_received = True
        order.is_delivered = True
        order.save()
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("store:index")
        # Redirect to the user dashboard or another appropriate page

    return redirect("user-dashboard")


def next_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    next_product = product.get_next_product()

    if next_product:
        data = {
            "title": next_product.title,
            "description": next_product.description,
            "price": next_product.price,
            "average_rating": next_product.average_rating(),
            "rating_count": next_product.ratings.count(),
            "slug": next_product.slug,
        }
    else:
        data = {}

    return JsonResponse(data)


def toggle_wishlist(request, product_id):
    next_url = request.GET.get("next")  # Define next_url early in the code
    product = get_object_or_404(Product, id=product_id)
    session_key = (
        get_session_key(request) if not request.user.is_authenticated else None
    )
    cart = Cart.objects.filter(product=product)
    if request.user.is_authenticated:
        if cart.exists:
            message = "this item is already in cart"
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )
    else:
        if cart.exists:
            message = "this item is already in cart"
        wishlist_item, created = Wishlist.objects.get_or_create(
            session_key=session_key, product=product
        )

    if created:
        message = "Added to wishlist"
        in_wishlist = True
    else:
        wishlist_item.delete()
        message = "Removed from wishlist"
        in_wishlist = False
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)
    return redirect("store:wishlist")

    # return JsonResponse({'message': message, 'in_wishlist': in_wishlist})


def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    next_url = request.GET.get("next")  # Define next_url early in the code
    print(f"Attempting to remove product: {product.title}")
    if request.user.is_authenticated:
        affected_rows = Wishlist.objects.filter(
            user=request.user, product=product
        ).delete()
    else:
        session_key = get_session_key(request)
        affected_rows = Wishlist.objects.filter(
            session_key=session_key, product=product
        ).delete()

    print(f"Deleted rows: {affected_rows}")
    messages.success(request, "deleted")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)
    return redirect("store:wishlist")


def wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
            "product"
        )
    else:
        session_key = get_session_key(request)
        wishlist_items = Wishlist.objects.filter(
            session_key=session_key
        ).select_related("product")

    # Debug: Check wishlist items
    print(f"Wishlist items: {[item.product.title for item in wishlist_items]}")

    # Fetch stock information
    for item in wishlist_items:
        try:
            item.stock_quantity = Stock.objects.get(product=item.product).quantity
        except Stock.DoesNotExist:
            item.stock_quantity = 0  # Handle case where stock is not found

    context = {"wishlist": wishlist_items}

    return render(request, "store/wishlist.html", context)


def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        session_key = get_session_key(request)
        count = Wishlist.objects.filter(session_key=session_key).count()

    return JsonResponse({"count": count})


class UpdateCartQuantity(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            cart_item_id = int(request.POST.get("cart_item_id"))
            quantity = request.POST.get("quantity")

            # Validate the quantity
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return JsonResponse({"message": "Invalid quantity"}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({"message": "Invalid quantity"}, status=400)

            # Fetch and update the cart item
            cart_item = get_object_or_404(Cart, id=cart_item_id, is_ordered=False)
            cart_item.quantity = quantity
            cart_item.save()

            # Check if cart_item has a size
            if cart_item.size is None:
                return JsonResponse(
                    {"message": "Size not found for this cart item"}, status=400
                )

            # Calculate the total quantity from the Size model for the same product
            product_sizes = cart_item.product.size.all()
            total_quantity = (
                product_sizes.aggregate(total_pieces=Sum("pieces"))["total_pieces"] or 0
            )

            # Determine if the wholesale price should be used
            if total_quantity >= cart_item.product.minimum_order:
                price_per_unit = cart_item.size.wholesale_price
            else:
                price_per_unit = (
                    cart_item.size.discount_price
                    if cart_item.size.discount_price
                    else cart_item.size.price
                )

            # Calculate the cart item total price based on the updated quantity and price
            cart_item_total = price_per_unit * quantity

            # Calculate the total price for all items in the cart
            if request.user.is_authenticated:
                cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
            else:
                session_cart_id = request.session.get("cart_id", None)
                cart_items = Cart.objects.filter(
                    session_key=session_cart_id, is_ordered=False
                )

            total_price = sum(item.get_total_price() for item in cart_items)

            # Fetch the order and calculate the total with delivery
            try:
                if request.user.is_authenticated:
                    order_qs = Order.objects.get(user=request.user, is_ordered=False)
                else:
                    order_qs = Order.objects.get(
                        session_key=session_cart_id, is_ordered=False
                    )
                total_order_and_delivery = order_qs.get_total_with_delivery()
            except Order.DoesNotExist:
                return JsonResponse({"message": "Order does not exist"}, status=404)

            return JsonResponse(
                {
                    "cart_item_id": cart_item_id,
                    "qty": quantity,
                    "total_order_and_delivery": int(total_order_and_delivery),
                    "cart_item_total": cart_item_total,
                    "total_order": total_price,
                    "total_quantity": total_quantity,
                    "messages": [
                        {"message": "Cart updated successfully", "tags": "success"}
                    ],
                }
            )

        return JsonResponse({"message": "error"}, status=400)


def handle_authenticated_user(request, product, size, color, quantity):
    with transaction.atomic():
        cart_item, created = Cart.objects.update_or_create(
            user=request.user,
            product=product,
            size=size,
            color=color,
            is_ordered=False,
            defaults={"quantity": quantity},
        )
        if created:
            Wishlist.objects.filter(product=product).delete()
            messages.success(request, f"{product.title} added to cart")
        else:
            messages.success(request, f"Updated {product.title} in cart")

        adjust_cart_item_price(cart_item, product, size, quantity)
        update_or_create_order(request, cart_item)
        Wishlist.objects.filter(user=request.user, product=product).delete()

        return prepare_response_data(request, cart_item)


import logging

logger = logging.getLogger(__name__)


def handle_unauthenticated_user(request, product, size, color, quantity):
    try:
        # Ensure session exists
        if not request.session.session_key:
            print("Session key missing, creating session.")
            request.session.create()

        session_cart_id = request.session.get("cart_id", None)

        # Check if session_cart_id exists or generate a new one
        if not session_cart_id:
            session_cart_id = str(uuid.uuid4())
            request.session["cart_id"] = session_cart_id
            request.session.modified = True
            print(f"New session_cart_id created: {session_cart_id}")
        else:
            print(f"Using existing session_cart_id: {session_cart_id}")

        print(f"Session Key: {request.session.session_key}, Cart ID: {session_cart_id}")

        # Try creating or updating the cart item
        cart_item, created = Cart.objects.update_or_create(
            session_key=session_cart_id,
            product=product,
            size=size,
            color=color,
            is_ordered=False,
            defaults={"quantity": quantity},
        )

        if created:
            print(f"Cart item created for anonymous user: {cart_item.id}")
        else:
            print(f"Cart item updated for anonymous user: {cart_item.id}")

        adjust_cart_item_price(cart_item, product, size, quantity)
        update_or_create_order(request, cart_item, session_cart_id)

        return prepare_response_data(request, cart_item)

    except Exception as e:
        logger.error(f"Error creating/updating cart item: {str(e)}")
        return {"message": f"Error: {str(e)}"}


def adjust_cart_item_price(cart_item, product, size, quantity):
    # Sum all the pieces for the sizes of the same product
    total_quantity = (
        Size.objects.filter(
            products=product  # `products` is the related name for the ManyToMany relationship with Product
        ).aggregate(total_pieces=Sum("pieces"))["total_pieces"]
        or 0
    )
    print({"total qty:": total_quantity})
    # Check if total pieces is greater than or equal to the product's minimum order
    if total_quantity >= product.minimum_order:
        cart_item.price = size.wholesale_price  # Use wholesale price
        print({"price is wholesale": cart_item.price})
        print({" minimum order is ": product.minimum_order})

    else:
        cart_item.price = size.discount_price  # Use discount price
        print({"the price is  discount": cart_item.price})
        print({" minimum order is ": product.minimum_order})
    cart_item.save()


def update_or_create_order(request, cart_item, cart_id=None):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            user=request.user,
            is_ordered=False,
            defaults={
                "reference": f"order-{secrets.token_hex(8)}",
                "date": timezone.now(),
            },
        )
    else:
        order, created = Order.objects.get_or_create(
            session_key=cart_id,
            is_ordered=False,
            defaults={
                "reference": f"order-{secrets.token_hex(8)}",
                "date": timezone.now(),
            },
        )

    if not order.product.filter(id=cart_item.id).exists():
        order.product.add(cart_item)
    order.save()


def prepare_response_data(request, cart_item):
    try:
        session_cart_id = request.session.get("cart_id")
        print(f"Preparing response data for cart ID: {session_cart_id}")

        cart_items = Cart.objects.filter(
            session_key=session_cart_id if not request.user.is_authenticated else None,
            user=request.user if request.user.is_authenticated else None,
            is_ordered=False,
        )

        cart_total = sum(item.get_total_price() for item in cart_items)
        total_order_and_delivery = None

        try:
            if request.user.is_authenticated:
                order = Order.objects.get(user=request.user, is_ordered=False)
            else:
                order = Order.objects.get(session_key=session_cart_id, is_ordered=False)

            total_order_and_delivery = order.get_total_with_delivery()
        except Order.DoesNotExist:
            total_order_and_delivery = None

        print(
            f"Cart Total: {cart_total}, Total Order + Delivery: {total_order_and_delivery}"
        )

        return {
            "success": True,
            "cart_total": float(cart_total),
            "total_order_and_delivery": (
                float(total_order_and_delivery) if total_order_and_delivery else None
            ),
            "cart_item_id": cart_item.id,
            "messages": [{"message": "Cart updated successfully", "tags": "success"}],
        }

    except Exception as e:
        logger.error(f"Error preparing response data: {str(e)}")
        return {"message": f"Error: {str(e)}"}


@csrf_exempt
@require_POST
def update_cart_color_and_qty(request):
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"message": "Invalid request"}, status=400)

    try:
        slug = request.POST.get("slug")
        size_id = request.POST.get("size")
        color_id = request.POST.get("color")
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(Product, slug=slug)
        size = get_object_or_404(Size, id=size_id) if size_id else None
        color = get_object_or_404(Color, id=color_id) if color_id else None

        print(f"Product: {product}, Size: {size}, Color: {color}, Quantity: {quantity}")

        if request.user.is_authenticated:
            print("Authenticated user detected.")
            # Log whether the user is authenticated
            response_data = handle_authenticated_user(
                request, product, size, color, quantity
            )
        else:
            print("Anonymous user detected.")
            response_data = handle_unauthenticated_user(
                request, product, size, color, quantity
            )
        # Ensure the response is serializable
        return JsonResponse(response_data, safe=False)

    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        return JsonResponse({"message": f"Error: {str(e)}"}, status=400)


class EmailSubscriptionView(View):
    def post(self, *args, **kwargs):
        email = self.request.POST.get("email")
        # Log the email input
        print(f"Received email: {email}")

        # Validate the email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(self.request, "Please enter a valid email address.")
            print("Invalid email address")
            return redirect(
                "store:subscribe_email"
            )  # Ensure 'subscribe_email' exists in your urls.py

        # Check if the email already exists in the database
        if EmailSubscription.objects.filter(email=email).exists():
            messages.error(self.request, "This email is already subscribed.")
            print("Email already subscribed")
        else:
            # Create and save the subscription
            EmailSubscription.objects.create(email=email)
            messages.success(self.request, "Thank you for subscribing!")
            print("Email subscription created successfully")

        # Redirect to the homepage or wherever you want after subscription
        return redirect("store:index")


def send_newsletter(request):
    subscribers = EmailSubscription.objects.all()
    email_list = [subscriber.email for subscriber in subscribers]

    if email_list:
        send_mail(
            subject="Our Latest News",
            message="Here is the latest news from our eCommerce store.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_list,
            fail_silently=False,
        )
        messages.success(
            request, f"Successfully sent emails to {len(email_list)} subscribers."
        )
    else:
        messages.error(request, "No subscribers found.")

    return redirect(
        "some_view"
    )  # Change 'some_view' to where you want to redirect after sending


def cancel_order(request, order_id):
    # Fetch the order
    order = get_object_or_404(Order, id=order_id)

    # Mark the order as canceled
    order.user_cancelled = True
    order.save()

    # Email subject and sender
    subject = f"Your Order #{order.reference} Has Been Canceled"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.user.email]

    # Create link for the user to continue the order
    continue_order_link = request.build_absolute_uri(
        reverse("store:continue_order", args=[order.id])
    )

    # Render email content
    html_message = render_to_string(
        "emails/user_order_canceled.html",
        {
            "order": order,
            "user": order.user,
            "continue_order_link": continue_order_link,
        },
    )
    plain_message = strip_tags(html_message)  # Fallback for non-HTML email clients

    # Send the email
    send_mail(
        subject, plain_message, from_email, recipient_list, html_message=html_message
    )

    # Redirect to the cart page after canceling the order
    return redirect("store:cart")


def continue_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Reactivate the order by setting the canceled status to False
    if order.user_cancelled:
        order.user_cancelled = False
        order.save()

    # Redirect the user to the checkout page
    return redirect("store:check-out")


from django.utils.timezone import make_aware

# class ViewOrders(View):
#     def get(self,request, *args, **kwargs):
#            # Fetch the original queryset
#         queryset = Order.objects.all()


#         # Get today's date (with timezone awareness if necessary)
#         today = make_aware(datetime.today())  # Assuming you use timezone-aware DateTimeField

#         # Filter queryset by today's date (ignoring time)
#         queryset = queryset.filter(date__date=today.date())

#         # Filter the queryset for revenue calculations
#         total_order_revenue = queryset.filter(is_ordered=True, deleted=False)

#         # Calculate total revenue
#         total_revenue = sum(order.get_total_with_delivery() for order in total_order_revenue)

#         # Get sales data for chart and pagination
#         sales_data = (
#             queryset.filter(is_ordered=True, deleted=False, cancelled=False)
#             )


#         # Extract the dates and quantities into separate lists for the chart

#         # Paginate the sales_data (for chart or other displayed data)
#         paginator = Paginator(sales_data, 20)  # Show 10 sales per page
#         page_number = request.GET.get('page') or 1  # Default to page 1 if no page is specified
#         page_obj = paginator.get_page(page_number)

#         extra_context = extra_context or {}

#         # Order counts and status-based filtering
#         extra_context['total_orders'] = queryset.filter(is_ordered=True).count()
#         extra_context['count'] = queryset.count()  # Total orders filtered for today
#         extra_context['pending_orders'] = queryset.filter(is_ordered=False).count()
#         extra_context['user_cancelled'] = queryset.filter(user_cancelled=True).count()
#         extra_context['delivered_orders'] = queryset.filter(is_delivered=True, is_ordered=True, is_received=True).count()
#         extra_context['undelivered_orders'] = queryset.filter(is_delivered=False, is_ordered=True, is_received=False).count()
#         extra_context['total_revenue'] = total_revenue
#         extra_context['sales_dates'] = dates
#         extra_context['page_obj'] = page_obj


#         # Data for charts
#         labels = ['Total Orders', 'Pending Orders', 'Delivered Orders', 'Undelivered Orders']
#         values = [
#             extra_context['total_orders'],
#             extra_context['pending_orders'],
#             extra_context['delivered_orders'],
#             extra_context['undelivered_orders']
#         ]

#         extra_context['chart_labels'] = labels
#         extra_context['chart_values'] = values


#         return render(request,'admins/orders/order_change_list.html', extra_context=extra_context)


#     # def changelist_view(self, request, extra_context=None):
#     #     # Fetch the original queryset
#     #     queryset = self.get_queryset(request)


#     #     # Get today's date (with timezone awareness if necessary)
#     #     today = make_aware(datetime.today())  # Assuming you use timezone-aware DateTimeField

#     #     # Filter queryset by today's date (ignoring time)
#     #     queryset = queryset.filter(date__date=today.date())

#     #     # Filter the queryset for revenue calculations
#     #     total_order_revenue = queryset.filter(is_ordered=True, deleted=False)

#     #     # Calculate total revenue
#     #     total_revenue = sum(order.get_total_with_delivery() for order in total_order_revenue)

#     #     # Get sales data for chart and pagination
#     #     sales_data = (
#     #         queryset.filter(is_ordered=True, deleted=False, cancelled=False)
#     #         )


#     #     # Extract the dates and quantities into separate lists for the chart

#     #     # Paginate the sales_data (for chart or other displayed data)
#     #     paginator = Paginator(sales_data, 20)  # Show 10 sales per page
#     #     page_number = request.GET.get('page') or 1  # Default to page 1 if no page is specified
#     #     page_obj = paginator.get_page(page_number)

#     #     extra_context = extra_context or {}

#     #     # Order counts and status-based filtering
#     #     extra_context['total_orders'] = queryset.filter(is_ordered=True).count()
#     #     extra_context['count'] = queryset.count()  # Total orders filtered for today
#     #     extra_context['pending_orders'] = queryset.filter(is_ordered=False).count()
#     #     extra_context['user_cancelled'] = queryset.filter(user_cancelled=True).count()
#     #     extra_context['delivered_orders'] = queryset.filter(is_delivered=True, is_ordered=True, is_received=True).count()
#     #     extra_context['undelivered_orders'] = queryset.filter(is_delivered=False, is_ordered=True, is_received=False).count()
#     #     extra_context['total_revenue'] = total_revenue
#     #     extra_context['sales_dates'] = dates
#     #     extra_context['page_obj'] = page_obj


#     #     # Data for charts
#     #     labels = ['Total Orders', 'Pending Orders', 'Delivered Orders', 'Undelivered Orders']
#     #     values = [
#     #         extra_context['total_orders'],
#     #         extra_context['pending_orders'],
#     #         extra_context['delivered_orders'],
#     #         extra_context['undelivered_orders']
#     #     ]

#     #     extra_context['chart_labels'] = labels
#     #     extra_context['chart_values'] = values

from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from datetime import datetime
from .models import Order


class ViewOrders(View):
    def get(self, request, *args, **kwargs):
        # Fetch the original queryset
        queryset = Order.objects.all()

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

        # Paginate the sales_data (for chart or other displayed data)
        paginator = Paginator(sales_data, 20)  # Show 20 sales per page
        page_number = (
            request.GET.get("page") or 1
        )  # Default to page 1 if no page is specified
        page_obj = paginator.get_page(page_number)

        # Order counts and status-based filtering
        total_orders = queryset.filter(is_ordered=True).count()
        count = queryset.count()  # Total orders filtered for today
        pending_orders = queryset.filter(is_ordered=False).count()
        user_cancelled = queryset.filter(user_cancelled=True).count()
        delivered_orders = queryset.filter(
            is_delivered=True, is_ordered=True, is_received=True
        ).count()
        undelivered_orders = queryset.filter(
            is_delivered=False, is_ordered=True, is_received=False
        ).count()

        # Data for charts
        chart_labels = [
            "Total Orders",
            "Pending Orders",
            "Delivered Orders",
            "Undelivered Orders",
        ]
        chart_values = [
            total_orders,
            pending_orders,
            delivered_orders,
            undelivered_orders,
        ]

        # Pass all context variables as a dictionary
        context = {
            "total_orders": total_orders,
            "count": count,
            "pending_orders": pending_orders,
            "user_cancelled": user_cancelled,
            "delivered_orders": delivered_orders,
            "undelivered_orders": undelivered_orders,
            "total_revenue": total_revenue,
            "page_obj": page_obj,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            # You need to define 'dates' here if you want to pass it for sales_dates
            "sales_dates": [],  # Placeholder for 'dates' if needed
        }

        return render(request, "admins/orders/order_change_list.html", context)


def delete_notification_action(
    self,
    request,
):
    # Delete notifications and return a JSON response for AJAX
    queryset = Notifications.objects.all()
    count = queryset.count()
    seen = queryset.filter(seen=False)
    seen.update = True
    queryset.delete()
    self.message_user(request, f"{count} notification(s) deleted.")
    return JsonResponse({"success": True, "deleted_count": count})


def notification_view(
    request,
):
    # Delete notifications and return a JSON response for AJAX
    queryset = Notifications.objects.all()
    return render(
        request,
        "admins/book_store/notifications/notice.html",
        {"notifications": queryset},
    )


class view_filtered_orders(View):
    def post(self, request, *args, **kwargs):
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
                return render(
                    request, "admins/orders/orders_filter_template.html", context
                )


def send_invoice(request, *args, **kwargs):

    try:
        order_id = request.POST.get("order_id")
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
            {"status": "error", "message": f"Error sending invoice: {e}"}, status=500
        )


class admin_cancel_order(View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if order.approved:
                messages.error(
                    request,
                    "Cannot cancel an approved order.",
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

                messages.success(
                    request,
                    f"Order {order.reference} canceled and email sent to the user.",
                )
        except Order.DoesNotExist:
            self.message_user(request, "Order does not exist.", level=messages.ERROR)

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

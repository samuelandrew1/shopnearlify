# helpers.py

from .models import *


def get_cart(request):
    cart = request.session.get("cart", {})
    return cart


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def add_to_cart(request, product_slug, quantity=1, size=None):
    cart = get_cart(request)
    if product_slug in cart:
        cart[product_slug]["quantity"] += quantity
        if size:
            cart[product_slug]["size"] = size
    else:
        cart[product_slug] = {"quantity": quantity, "size": size}
    save_cart(request, cart)


def update_cart_item(request, product_slug, quantity, size):
    cart = get_cart(request)
    if product_slug in cart:
        cart[product_slug]["quantity"] = quantity
        cart[product_slug]["size"] = size
        save_cart(request, cart)
        return True
    return False


def remove_from_cart(request, product_slug):
    cart = get_cart(request)
    if product_slug in cart:
        del cart[product_slug]
        save_cart(request, cart)
        return True
    return False

# store/templatetags/cart_tags.py
from django import template
from store.models import Cart, Order

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_info(context):
    request = context["request"]

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        order = Order.objects.filter(user=request.user, is_ordered=False).first()
    else:
        session_cart_id = request.session.get("cart_id")
        cart_items = Cart.objects.filter(cart_id=session_cart_id, is_ordered=False)
        order = Order.objects.filter(cart_id=session_cart_id, is_ordered=False).first()

    total = order.get_total_with_delivery() if order else 0

    return {
        "cart_items": cart_items,
        "total": total,
    }

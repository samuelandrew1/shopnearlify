from django import template
from django import template
from store.models import Cart, Order

register = template.Library()


@register.simple_tag(takes_context=True)
def cart_item_count(context):
    request = context["request"]
    if request.user.is_authenticated:
        # Count cart items for authenticated users
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        return cart_items.count()


@register.filter
def cart_total(request):
    if request.user.is_authenticated:
        queryset = Cart.objects.filter(user=request.user, is_ordered=False)
    else:
        cart_uuid = request.session.get("cart_uuid")
        if cart_uuid:
            queryset = Cart.objects.filter(cart_uuid=cart_uuid, is_ordered=False)
        else:
            queryset = Cart.objects.none()
    return queryset


@register.filter
def get_total(user):
    queryset = Order.objects.all().filter(user=user)
    return queryset

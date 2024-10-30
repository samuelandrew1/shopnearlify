from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, Order
import uuid

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


@receiver(user_logged_in)
def transfer_cart_from_session_to_user(sender, request, user, **kwargs):
    session_cart_id = request.session.get("cart_id")
    if not session_cart_id:
        return

    # Retrieve all cart items associated with the session_cart_id
    session_cart_items = Cart.objects.filter(
        session_key=session_cart_id, is_ordered=False
    )

    if not session_cart_items.exists():
        return

    # Check if the user already has an open order
    user_order, order_created = Order.objects.get_or_create(user=user, is_ordered=False)

    for item in session_cart_items:
        # Check if the user already has this item in their cart
        user_cart_item, cart_created = Cart.objects.get_or_create(
            user=user, product=item.product, size=item.size, is_ordered=False
        )
        if cart_created:
            # If a new cart item was created, set the quantity to the session cart item's quantity
            user_cart_item.quantity = item.quantity
        else:
            # If the item already exists in the user's cart, increase the quantity
            user_cart_item.quantity += item.quantity

        user_cart_item.save()

        # Add the cart item to the user's order if it's not already added
        if user_cart_item not in user_order.product.all():
            user_order.product.add(user_cart_item)

    # Clear the session cart
    session_cart_items.delete()
    del request.session["cart_id"]
    request.session.modified = True

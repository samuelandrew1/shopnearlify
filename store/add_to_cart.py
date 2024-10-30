# helpers.py

from .models import Product


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


@csrf_exempt
@require_POST
def add_to_cart(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        slug = request.POST.get("slug")
        size_id = request.POST.get("size")
        color_id = request.POST.get("color")
        quantity = int(request.POST.get("quantity", 1))
        product = get_object_or_404(Product, slug=slug)
        size = get_object_or_404(Size, id=size_id) if size_id else None
        color = get_object_or_404(Color, id=color_id) if color_id else None

        if request.user.is_authenticated:
            cart_qs = Cart.objects.filter(
                user=request.user,
                product=product,
                size=size,
                color=color,
                is_ordered=False,
            )

            if cart_qs.exists():
                cart_item = cart_qs.first()
                cart_item.quantity += quantity
                cart_item.save()
                # messages.success(request, f"Updated {product.title} in cart")
            else:
                cart_item = Cart.objects.create(
                    user=request.user,
                    product=product,
                    size=size,
                    color=color,
                    quantity=quantity,
                    is_ordered=False,
                )
                messages.success(request, f"{product.title} added to cart")
            order, created = Order.objects.get_or_create(
                user=request.user,
                is_ordered=False,
                defaults={
                    "reference": f"order-{secrets.token_hex(8)}",
                    "date": timezone.now(),
                },
            )
            if not order.product.filter(id=cart_item.id).exists():
                order.product.add(cart_item)
            order.save()

            Wishlist.objects.filter(user=request.user, product=product).delete()

            storage = get_messages(request)
            response_messages = [
                {"message": message.message, "tags": message.tags}
                for message in storage
            ]

            cart_count = Cart.objects.filter(
                user=request.user, is_ordered=False
            ).count()

            return JsonResponse(
                {
                    "success": True,
                    "cart_count": cart_count,
                    "messages": response_messages,
                }
            )
        else:
            session_cart_id = request.session.get("cart_id")
            if not session_cart_id:
                session_cart_id = str(uuid.uuid4())
                request.session["cart_id"] = session_cart_id
                request.session.modified = True

            cart_qs = Cart.objects.filter(
                cart_id=session_cart_id,
                product=product,
                size=size,
                color=color,
                is_ordered=False,
            )
            if cart_qs.exists():
                cart_item = cart_qs.first()
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f"Updated {product.title} in cart")
            else:
                cart_item = Cart.objects.create(
                    cart_id=session_cart_id,
                    product=product,
                    size=size,
                    color=color,
                    quantity=quantity,
                    is_ordered=False,
                )
                messages.success(request, f"{product.title} added to cart")

            order, created = Order.objects.get_or_create(
                cart_id=session_cart_id,
                is_ordered=False,
                defaults={
                    "reference": f"order-{secrets.token_hex(8)}",
                    "date": timezone.now(),
                },
            )
            if not order.product.filter(id=cart_item.id).exists():
                order.product.add(cart_item)
            order.save()

            storage = get_messages(request)
            response_messages = [
                {"message": message.message, "tags": message.tags}
                for message in storage
            ]

            cart_count = Cart.objects.filter(
                cart_id=session_cart_id, is_ordered=False
            ).count()

            return JsonResponse(
                {
                    "success": True,
                    "cart_count": cart_count,
                    "messages": response_messages,
                }
            )
    return JsonResponse({"message": "Error processing your request"}, status=400)

@csrf_exempt
@require_POST
def add_to_cart(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        slug = request.POST.get("slug")
        product = get_object_or_404(Product, slug=slug)
        quantity = int(
            request.POST.get("quantity", 1)
        )  # Default quantity to 1 if not provided

        if request.user.is_authenticated:
            cart_qs = Cart.objects.filter(
                user=request.user, product=product, is_ordered=False
            )

            if cart_qs.exists():
                cart_item = cart_qs.first()
                cart_item.quantity += quantity  # Increment the quantity
                cart_item.save()
                messages.success(request, f"Updated {product.title} quantity in cart")
            else:
                cart_item = Cart.objects.create(
                    user=request.user,
                    product=product,
                    quantity=quantity,
                    is_ordered=False,
                )
                messages.success(request, f"{product.title} is added to cart")

            # Create or update the order
            order_qs = Order.objects.filter(user=request.user, is_ordered=False)
            if order_qs.exists():
                order = order_qs.first()
            else:
                order = Order.objects.create(
                    user=request.user,
                    reference=f"order-{secrets.token_hex(8)}",
                    date=timezone.now(),
                    is_ordered=False,
                )

            order.product.add(cart_item)
            order.save()

            storage = get_messages(request)
            response_messages = [
                {"message": message.message, "tags": message.tags}
                for message in storage
            ]

            return JsonResponse(
                {
                    "success": True,
                    "cart_count": Cart.objects.filter(
                        user=request.user, is_ordered=False
                    ).count(),
                    "messages": response_messages,
                }
            )
        else:
            # Handle cart for anonymous users
            cart = request.session.get("cart", {})

            if str(product.id) in cart:
                cart[str(product.id)]["quantity"] += quantity
                messages.success(request, f"Updated {product.title} quantity in cart")
            else:
                cart[str(product.id)] = {
                    "product_id": product.id,
                    "title": product.title,
                    "quantity": quantity,
                }
                messages.success(request, f"{product.title} is added to cart")

            request.session["cart"] = cart
            request.session.modified = True  # Ensure session is saved

            storage = get_messages(request)
            response_messages = [
                {"message": message.message, "tags": message.tags}
                for message in storage
            ]

            return JsonResponse(
                {
                    "success": True,
                    "cart": request.session.get("cart", {}),
                    "messages": response_messages,
                }
            )

    return JsonResponse({"message": "error processing your request"}, status=400)


import secrets
from django.db import models
from django.conf import settings
from django.utils import dates
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.sessions.models import Session
from star_ratings.models import Rating
import uuid
from django.db.models import Avg
from django.urls import reverse

category_choices = (
    ("new", "new"),
    ("featured", "featured"),
    ("promo", "promo"),
    ("ankara", "ankara"),
    ("shoes", "shoes"),
)

payment_choices = (
    ("paypal", "paypal"),
    ("paystack", "paystack"),
)


label_choices = (
    ("label-new", "new"),
    ("label-out", "out"),
    ("label-top", "top"),
    ("label-sale", "sale"),
)
gender_choices = (
    ("Male", "male"),
    ("Female", "female"),
)


class ProductManager(models.Manager):
    def get_top_products(self, limit=3):
        return self.filter(is_best_selling=True)[:limit]

    def get_trending_products_by_category(self, category_slug, limit=3):
        return self.filter(category__slug=category_slug).order_by("-ratings__rating")[
            :limit
        ]

    def get_top_selling_by_category(self, limit=5):
        categories = Category.objects.all()
        top_selling_products = []

        for category in categories:
            products = self.filter(category=category).order_by("-label")[:5]
            top_selling_products.append({"category": category, "products": products})

        return top_selling_products

    def get_products_by_label(self, limit=5):
        labels = [choice[0] for choice in label_choices]
        products_by_label = []

        for label in labels:
            products = self.filter(label=label)[:limit]
            products_by_label.append({"label": label, "products": products})

        return products_by_label

    def get_new_products(self, limit=5):
        return self.filter(label="label-new")[:limit]

    def get_top_discounted_products(self, limit=3):
        return (
            self.annotate(
                discount_amount=models.F("price") - models.F("discount_price")
            )
            .filter(discount_price__gt=0)
            .order_by("-discount_amount")[:limit]
        )


class Category(models.Model):
    title = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(default="")
    img = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )

    def save(self, *args, **kwargs):
        self.slug = self.slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("store:categories-filter", kwargs={"slug": self.slug})


class Features(models.Model):
    feature1 = models.CharField(max_length=255, blank=True, null=True)
    feature2 = models.CharField(max_length=255, blank=True, null=True)
    feature3 = models.CharField(max_length=255, blank=True, null=True)
    feature4 = models.CharField(max_length=255, blank=True, null=True)
    feature5 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.feature1


class Size(models.Model):
    size = models.CharField(max_length=10, unique=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self) -> str:
        return self.size


class Color(models.Model):
    name = models.CharField(max_length=50)
    img = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    quantity = models.IntegerField(default=1, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    additional_information = models.TextField(max_length=1000, default="")
    size = models.ManyToManyField(Size, related_name="products")
    price = models.IntegerField(default=0)
    discount_price = models.IntegerField(default=0)
    wholesale_price = models.IntegerField(default=0)
    img_1 = models.ImageField(upload_to="static/media/img", default="img")
    img_2 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    img_3 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    img_4 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    color = models.ManyToManyField(Color)
    label = models.CharField(
        choices=label_choices, max_length=255, default="", blank=True
    )
    features = models.ForeignKey(
        Features, on_delete=models.CASCADE, blank=True, null=True
    )
    category = models.ForeignKey(Category, default="", on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=10, choices=gender_choices, default="female", blank=True, null=True
    )
    display_on_home_page = models.BooleanField(default=False)
    is_banner = models.BooleanField(default=False)
    is_best_selling = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, default="eg-product-title")
    ratings = Rating()
    objects = ProductManager()  # Attach the custom manager
    is_featured = models.BooleanField(default=False)
    is_deal_of_the_day = models.BooleanField(default=False)
    quantity_sold = models.PositiveIntegerField(default=0)
    minimum_order = models.IntegerField(default=1)

    def is_on_sale(self):
        return self.discount_price > 0

    @staticmethod
    def get_products_on_sale():
        return Product.objects.filter(
            label="sale"
        )  # Filter products with discount price

    @staticmethod
    def get_featured_products():
        return Product.objects.filter(is_featured=True)[:4]

    @staticmethod
    def get_deal_of_the_day_products():
        return Product.objects.filter(is_deal_of_the_day=True)[:1]

    @staticmethod
    def get_top_rated_products():
        return Product.objects.annotate(avg_rating=Avg("ratings__rating")).order_by(
            "-avg_rating"
        )[:5]

    def get_stock_status(self):
        stock = Stock.objects.filter(product=self).first()
        if stock:
            return stock.quantity
        return 0

    # qty = models.IntegerField(default=1)
    def get_add_to_wishlist_url(self):
        return reverse("store:add-to-wishlist", kwargs={"product_id": self.id})

    def get_remove_from_wishlist_url(self):
        return reverse("store:remove-from-wishlist", kwargs={"product_id": self.id})

    def get_related_products(self):
        return Product.objects.filter(category=self.category).exclude(id=self.id)[
            :4
        ]  # Change the number of products to display as needed

    def get_absolute_url(self):
        return reverse("store:product-detail", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("store:add-to-cart", kwargs={"slug": self.slug})

    def delete_cart(self):
        return reverse(
            "store:delete-cart-item",
            kwargs={
                "slug": self.slug,
            },
        )

    def get_human_readable_label(self):
        return dict(label_choices).get(self.label, "")

    # def get_cart_increment(self):
    #     return reverse("store:reduce_cart", kwargs={"slug": self.slug,})

    # def get_cart_increment(self):
    #     return reverse("store:increase_cart", kwargs={"slug": self.slug,})

    def __str__(self):
        return f"{self.title}"

    def average_rating(self):
        ratings = self.ratings.all()

        if ratings:
            return sum(rating.rating for rating in ratings) / ratings.count()
        return 0

    # get the next product by clicking the next button
    def get_next_product(self):
        next_product = Product.objects.filter(id__gt=self.id).order_by("id").first()
        if not next_product:
            next_product = Product.objects.order_by("id").first()
        return next_product


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product"
    )
    quantity = models.IntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    is_in_cart = models.BooleanField(default=False)
    cart_id = models.UUIDField(
        default=uuid.uuid4,
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)

    def get_discount_price(self):
        return self.quantity * self.product.discount_price

    def get_normal_price(self):
        return self.quantity * self.product.price

    def get_amount_saved(self):
        return self.get_normal_price() - self.get_discount_price()

    def get_price_tag(self):
        discount_price = self.product.discount_price
        normal_price = self.product.price
        if discount_price:
            return discount_price
        return normal_price

    def get_total_price(self):
        if self.get_discount_price():
            return self.get_discount_price()
        return self.get_normal_price()

    def add_quantity(self):
        qty = self.quantity
        qty += 1
        return qty

    def __str__(self):
        price = self.product.price
        dis_count_price = self.product.discount_price
        title = self.product.title
        if not dis_count_price:
            return f"item: {title}, price: {price}, quantity: {self.quantity}, color:{self.color.name}, size {self.size.size}"
        return f"item:{title} price: {dis_count_price}, quantity: {self.quantity}, color: {self.color.name if self.color else None}, size {self.size.size}"

    def get_title(self):
        return self.product.title


address_choices = (("shipping", "shipping Address"), ("billing", "billing Address"))

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number  must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)


class CartColor(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.color.name} {self.quantity}"


class CustomersAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
        blank=True,
        null=True,
    )
    street_address = models.CharField(max_length=300)
    apartment = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    telephone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    zip_code = models.CharField(max_length=20)
    # country = CountryField(multiple=False)
    country = models.CharField(max_length=20, default="Nigeria")
    message = models.TextField(max_length=500, null=True, blank=True)
    # payment_option = models.CharField(max_length=255, choices=payment_choices, blank=True,null=True)

    def __str__(self):
        return f"{self.user.username}:   address is {self.street_address}"

    def get_absolute_url(self):
        return reverse("store:update-address", kwargs={"pk": self.pk})


class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=""
    )
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_created",)

    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(10)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref

        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount) * 100


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    amount = models.IntegerField(
        default=0,
    )
    valid_from = models.DateTimeField(default=timezone.now())
    valid_to = models.DateTimeField(default=timezone.now(), blank=True, null=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
        blank=True,
        null=True,
    )
    is_used = models.BooleanField(default=False)
    used_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="used_coupons", blank=True
    )

    def __str__(self) -> str:
        return f"{self.code}   {self.amount}"


del_status = (
    ("processing", "processing"),
    ("in_progress", "in_progress"),
    ("delivered", "delivered"),
)


class AbujaLocation(models.Model):
    location = models.CharField(max_length=255)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    days = models.IntegerField(default=2)

    def __str__(self):
        return self.location


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default="",
        null=True,
        blank=True,
    )
    is_ordered = models.BooleanField(default=False)
    product = models.ManyToManyField(
        Cart,
    )
    reference = models.CharField(max_length=50, default="")
    shipping_address = models.ForeignKey(
        CustomersAddress, on_delete=models.SET_NULL, blank=True, null=True
    )
    Payment = models.ForeignKey(
        Payment, on_delete=models.PROTECT, blank=True, null=True
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    is_delivered = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    is_refund_request = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.datetime.now())
    delivery_status = models.CharField(
        max_length=255, default="Processing", choices=del_status
    )
    abuja_location = models.ForeignKey(
        AbujaLocation, on_delete=models.SET_NULL, blank=True, null=True
    )
    cart_id = models.UUIDField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        user = self.user
        session_key = self.session_key
        return f"{user if user else session_key}"

    # display the quantity in table
    def quantity(self):
        for items in self.product.all():
            return items.quantity
        return None

    def get_total(self):
        total = 0
        for item in self.product.all():
            total += item.get_total_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_coupon(self):

        return self.get_total() - self.coupon.amount

        # display the product title in datable

    def number_of_items(self):
        queryset = Cart.objects.filter(user=self.user, is_ordered=False).count()
        if queryset == 0:
            return "-"
        return queryset

    def items(self):
        queryset = self.product.count()
        if queryset == 0:
            return "-"
        return queryset

        # get the price in the order

    def total_price(self):
        return self.get_total()

    def get_delivery_cost(self):  # calculates the delivery cost
        if self.abuja_location:
            return self.abuja_location.delivery_cost
        return 0

    def get_total_with_delivery(self):
        return self.get_total() + self.get_delivery_cost()


class Refunds(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField(default="")
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self) -> str:
        return f"{self.order} {self.reason}"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.product} {self.quantity}"


class CustomerRating(models.Model):
    headline = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="ratings", on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(max_length=500, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.rating}"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    # Add more fields as per your requirement (e.g., customer information, itemized details, etc.)

    def __str__(self):
        return self.invoice_number


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product", "session_key")

    def __str__(self):
        return f"{self.user or self.session_key} - {self.product.title}"


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.product.title} {self.quantity}"

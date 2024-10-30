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
from django.db.models import F, OuterRef, Subquery
from django.db.models import Avg, Count, Sum
from django.utils.http import urlencode
from django.contrib.auth.models import AbstractUser
from django.db import models
from delivery.models import DeliveryLocations
from paystack_api.models import Payment
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(region="NG", blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


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
from django.contrib.auth.models import AbstractUser


#
class SizeManager(models.Manager):
    def get_top_discounted_sizes(self, limit=3):
        return (
            self.annotate(discount_amount=F("price") - F("discount_price"))
            .filter(discount_price__gt=0)
            .order_by("-discount_amount")[:limit]
        )


class ProductManager(models.Manager):
    def get_top_products(self, limit=3):
        return self.filter(is_best_selling=True)[:limit]

    def get_trending_products_by_category(self, category_slug, limit=3):
        return self.filter(category__slug=category_slug).order_by("-ratings__rating")[
            :limit
        ]

    @staticmethod
    def get_top_selling_by_category(limit=10):
        # Ensure products have at least one sale
        return (
            Product.objects.annotate(total_quantity_sold=Sum("quantity_sold"))
            .filter(total_quantity_sold__gt=0)
            .order_by("-total_quantity_sold")[:limit]
        )

    def get_products_by_label(self, limit=10):
        labels = [choice[0] for choice in label_choices]
        products_by_label = []

        for label in labels:
            products = self.filter(label=label)[:limit]
            products_by_label.append({"label": label, "products": products})

        return products_by_label

    def get_new_products(self, limit=5):
        return self.filter(label="label-new")[:limit]

    # def get_top_discounted_products(self, limit=3):
    #     return self.annotate(discount_amount=models.F('price') - models.F('discount_price')) \
    #                .filter(discount_price__gt=0) \
    #                .order_by('-discount_amount')[:limit]

    def get_top_discounted_products(self, limit=3):
        size_subquery = (
            Size.objects.filter(product_id=OuterRef("pk"))
            .annotate(discount_amount=F("price") - F("discount_price"))
            .order_by("-discount_amount")
            .values("discount_amount")[:1]
        )

        return self.annotate(top_discount_amount=Subquery(size_subquery)).order_by(
            "-top_discount_amount"
        )[:limit]


class Category(models.Model):
    title = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(default="")
    img = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )

    # def save(self, *args, **kwargs):
    #     self.slug = self.slug
    #     super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("store:categories-filter", kwargs={"slug": self.slug})


class Color(models.Model):
    name = models.CharField(max_length=50)
    img = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    stock = models.IntegerField(default=1, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    size = models.CharField(max_length=10, unique=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    discount_price = models.IntegerField(default=0)
    wholesale_price = models.IntegerField(default=0)
    pieces = models.IntegerField(default=0)
    objects = SizeManager()
    product_colors = models.ManyToManyField(
        Color, through="ProductSizeColor", related_name="size_colors"
    )

    def __str__(self) -> str:
        return self.size


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(
        max_length=255,
    )
    feature1 = models.CharField(max_length=255, blank=True, null=True)
    feature2 = models.CharField(max_length=255, blank=True, null=True)
    feature3 = models.CharField(max_length=255, blank=True, null=True)
    feature4 = models.CharField(max_length=255, blank=True, null=True)
    feature5 = models.CharField(max_length=255, blank=True, null=True)
    feature6 = models.CharField(max_length=255, blank=True, null=True)
    feature7 = models.CharField(max_length=255, blank=True, null=True)
    feature8 = models.CharField(max_length=255, blank=True, null=True)
    feature8 = models.CharField(max_length=255, blank=True, null=True)
    feature10 = models.CharField(max_length=255, blank=True, null=True)
    specification1 = models.CharField(max_length=255, blank=True, null=True)
    specification2 = models.CharField(max_length=255, blank=True, null=True)
    specification3 = models.CharField(max_length=255, blank=True, null=True)
    specification4 = models.CharField(max_length=255, blank=True, null=True)
    specification5 = models.CharField(max_length=255, blank=True, null=True)
    specification6 = models.CharField(max_length=255, blank=True, null=True)
    specification7 = models.CharField(max_length=255, blank=True, null=True)
    specification8 = models.CharField(max_length=255, blank=True, null=True)
    specification9 = models.CharField(max_length=255, blank=True, null=True)
    specification10 = models.CharField(max_length=255, blank=True, null=True)

    size = models.ManyToManyField(
        Size, related_name="products", through="ProductSizeColor"
    )
    img_1 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    img_2 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    img_3 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    img_4 = models.ImageField(
        upload_to="static/media/img", default="img", blank=True, null=True
    )
    color = models.ManyToManyField(Color, through="ProductSizeColor")
    label = models.CharField(
        choices=label_choices, max_length=255, default="", blank=True
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

    @property
    def total_stock(self):
        return self.color.aggregate(total_stock=Sum("stock"))["total_stock"] or 0

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
    def get_top_selling_by_category():
        categories = Category.objects.all()
        top_selling = {}
        for category in categories:
            # Fetch products with quantity_sold greater than 0 and order them by quantity_sold
            top_selling_products = Product.objects.filter(
                category=category, quantity_sold__gt=0
            ).order_by("-quantity_sold")[:5]

            # If the queryset is empty, skip the category
            if top_selling_products.exists():
                top_selling[category.title] = top_selling_products
            else:
                top_selling[category.title] = (
                    None  # or [] to indicate no top-selling products
                )

        return top_selling

    def get_full_url(self):
        # Assuming you're using the request object to get the full URL
        from django.contrib.sites.models import Site

        current_site = Site.objects.get_current()
        return f"https://{current_site.domain}{self.get_absolute_url()}"

    def get_facebook_share_url(self):
        share_url = self.get_full_url()
        return (
            f"https://www.facebook.com/sharer/sharer.php?{urlencode({'u': share_url})}"
        )

    def get_twitter_share_url(self):
        share_url = self.get_full_url()
        text = f"Check out this product: {self.title}"
        return f"https://twitter.com/intent/tweet?{urlencode({'url': share_url, 'text': text})}"

    def get_whatsapp_share_url(self):
        share_url = self.get_full_url()
        text = f"Check out this product: {self.title} - {share_url}"
        return f"https://api.whatsapp.com/send?{urlencode({'text': text})}"

    def get_linkedin_share_url(self):
        share_url = self.get_full_url()
        return f"https://www.linkedin.com/shareArticle?{urlencode({'url': share_url, 'title': self.title})}"

    def get_email_share_url(self):
        share_url = self.get_full_url()
        subject = f"Check out this product: {self.title}"
        body = f"Check out this product on our website: {self.title} - {share_url}"
        return f"mailto:?{urlencode({'subject': subject, 'body': body})}"

    @staticmethod
    def get_top_rated_products():
        return (
            Product.objects.annotate(
                average_rating=Avg("ratings__rating"), review_count=Count("ratings")
            )
            .filter(review_count__gt=0)
            .order_by("-average_rating")[:5]
        )

    def get_stock_status(self):
        stock = Stock.objects.filter(product=self).first()
        if stock:
            return stock.quantity
        return 0

    # qty = models.IntegerField(default=1)
    def get_add_to_wishlist_url(self):
        return reverse("store:add-to-wishlist", kwargs={"product_id": self.id})

    def get_remove_from_wishlist_url(self):
        return reverse("store:remove-from-wishlist", kwargs={"product_id": self.pk})

    def get_related_products(self):
        return Product.objects.filter(category=self.category).exclude(id=self.id)[
            :5
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


class ProductSizeColor(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_size_colors"
    )
    size = models.ForeignKey(
        Size, on_delete=models.CASCADE, related_name="size_product_colors"
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="color_product_colors", default=""
    )

    class Meta:
        unique_together = ("product", "size", "color")

    def __str__(self):
        return f"{self.product.title} - {self.size.size} - {self.color.name if self.color.name else None}"


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
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
    cancelled = models.BooleanField(default=False)

    def get_discount_price(self):
        if self.size and self.size.discount_price:
            return self.quantity * self.size.discount_price
        return self.quantity * self.size.price

    def get_normal_price(self):
        if self.size:
            return self.quantity * self.size.price
        return 0

    def get_total_price(self):
        if self.size:
            return self.get_discount_price()
        return self.get_normal_price()

    def get_discount_price(self):
        if self.size and self.size.discount_price:
            return self.quantity * self.size.discount_price
        return self.quantity * self.size.price

    # def get_normal_price(self):
    #     if self.size:
    #         return self.quantity * self.size.price
    #     return 0

    def get_amount_saved(self):
        return self.get_normal_price() - self.get_discount_price()

    def get_price_tag(self):
        if self.size:
            discount_price = self.size.discount_price
            normal_price = self.size.price
            if discount_price:
                return discount_price
            return normal_price
        return 0

    def get_total_price(self):
        if self.size:
            size = self.size
            product = self.product
            quantity = self.quantity
            # Apply wholesale price if quantity meets or exceeds the minimum order
            if size.pieces >= product.minimum_order:
                price = size.wholesale_price
            else:
                # Check if retail price or discount price should be applied
                if size.discount_price:  # If there's a discount price, apply it
                    price = size.discount_price
                else:
                    price = size.price  # Apply retail price if no discount is available

            return price * quantity  # Return the price based on the quantity
        return 0

    def add_quantity(self):
        self.quantity += 1
        return self.quantity

    def __str__(self):
        if self.size:  # Check if size is not None
            price = (
                self.size.discount_price
                if self.size.discount_price
                else self.size.price
            )
        else:
            price = "No size available"  # Handle the case where size is None
        return f"{self.product.title} - {price}"

    def get_title(self):
        return self.product.title


address_choices = (("shipping", "shipping Address"), ("billing", "billing Address"))


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
        related_name="users",
    )
    street_address = models.CharField(max_length=300)
    apartment = models.CharField(max_length=255)
    town = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    state = models.CharField(max_length=50, default="")
    telephone = PhoneNumberField(region="NG")
    zip_code = models.CharField(max_length=20)
    country = CountryField(blank_label="(select country)")
    # country = models.CharField(max_length=20, default='Nigeria')
    message = models.TextField(max_length=500, null=True, blank=True)
    # payment_option = models.CharField(max_length=255, choices=payment_choices, blank=True,null=True)

    def __str__(self):
        return f"{self.street_address}, {self.apartment}, {self.telephone}, {self.state}, {self.zip_code}"

    def get_absolute_url(self):
        return reverse("store:update-address", kwargs={"pk": self.pk})


class Coupon(models.Model):
    code = models.CharField(max_length=50)
    amount = models.IntegerField(
        default=0,
    )
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now, blank=True, null=True)
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
    delivery_location = models.ForeignKey(
        DeliveryLocations, on_delete=models.SET_NULL, blank=True, null=True
    )
    cart_id = models.UUIDField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    approved = models.BooleanField(default=False)
    user_cancelled = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate invoice number if not set
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        user = self.user
        session_key = self.session_key
        return f"{user if user else session_key}"

    # display the quantity in table
    def quantity(self):
        for items in self.product.all():
            return items.quantity
        return None

    # def get_total(self):
    #     total = 0
    #     for item in self.product.all():
    #         total += item.get_total_price()
    #     if self.coupon:
    #         total -= self.coupon.amount
    #     return total

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

    def get_total(self):
        total = 0
        for cart_item in self.product.all():
            # Use the total price from the cart item's get_total_price method
            total += cart_item.get_total_price()

        # Apply coupon discount if available
        if self.coupon:
            total -= self.coupon.amount

        return total

    # def get_total_with_delivery(self):
    #     return self.get_total() + self.get_delivery_cost()
    def get_total_with_delivery(self):
        # Replace these with your actual logic for calculating
        total_price = self.get_total()  # Assuming this method exists
        delivery_fee = self.get_delivery_cost()  # Assuming this method exists
        return total_price + delivery_fee

    def get_delivery_cost(self):
        if self.delivery_location:
            return self.delivery_location.delivery_cost
        return 0

    def get_delivery_cost(self):
        if self.delivery_location:
            return self.delivery_location.delivery_cost
        return 0


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


class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


from datetime import datetime


class Notifications(models.Model):
    title = models.CharField(
        max_length=200,
    )
    date = models.DateTimeField(default=timezone.datetime.today())
    seen = models.BooleanField(default=False)

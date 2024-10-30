from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from book_store.models import Cart, Order, CustomersAddress, Product, Rating, Category
from store.form import UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from delivery.deliveryform import AddressForm
from django.contrib.messages import get_messages
from django.test import TestCase, Client


User = get_user_model()


class DashBoardViewTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )

        # Create a session for the anonymous user
        self.client = Client()
        session = self.client.session
        session.save()  # Saving the session to store the cart for an anonymous user
        self.category = Category.objects.create(title="tv", slug="tv")
        # Create a product
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            description=" this is the test product",
            category=self.category,
            # Adjust the product fields based on your model
        )

        # Create an order and cart for the authenticated user
        self.order = Order.objects.create(user=self.user, is_ordered=True)
        self.auth_cart = Cart.objects.create(
            user=self.user, product=self.product, is_ordered=False
        )  # Authenticated user's cart

        # Create a cart for the anonymous user (session-based)
        self.anon_cart = Cart.objects.create(
            session_key=session.session_key, product=self.product, is_ordered=False
        )  # Anonymous user's cart

        # Create an address for the authenticated user
        self.address = CustomersAddress.objects.create(
            user=self.user, street_address="123 Test St", city="Test City"
        )

        # Create a reviewed product and rating
        # Rating.objects.create(user=self.user, product=self.product, rating=5)

    def test_dashboard_get_authenticated_user(self):
        # Log the user in
        self.client.login(username="testuser", password="testpassword")

        # Simulate a GET request to the dashboard view for authenticated user
        response = self.client.get(reverse("store:dash-board"))

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the context contains the correct data for authenticated user
        self.assertIsInstance(response.context["profile_form"], UserProfileForm)
        self.assertIsInstance(response.context["password_form"], PasswordChangeForm)
        self.assertIsInstance(response.context["address_form"], AddressForm)
        self.assertQuerysetEqual(
            response.context["orders"],
            Order.objects.filter(user=self.user, is_ordered=True),
            transform=lambda x: x,
        )
        self.assertQuerysetEqual(
            response.context["cart"],
            Cart.objects.filter(user=self.user, is_ordered=False),
            transform=lambda x: x,
        )
        self.assertEqual(response.context["address"], self.address)

    def test_dashboard_get_anonymous_user(self):
        # Simulate a GET request to the dashboard view for anonymous user
        response = self.client.get(reverse("store:dash-board"))

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the context contains the correct data for anonymous user
        self.assertIsNone(
            response.context.get("profile_form")
        )  # No profile form for anonymous users
        self.assertIsNone(
            response.context.get("password_form")
        )  # No password change form for anonymous users
        self.assertQuerysetEqual(
            response.context["cart"],
            Cart.objects.filter(
                session_key=self.client.session.session_key, is_ordered=False
            ),
            transform=lambda x: x,
        )
        self.assertIsNone(
            response.context.get("orders")
        )  # Anonymous users don't have orders

    def test_dashboard_post_update_profile_authenticated(self):
        # Log the user in
        self.client.login(username="testuser", password="testpassword")

        # Simulate a POST request to update the profile for authenticated user
        response = self.client.post(
            reverse("store:dash-board"),
            {
                "update_profile": "true",
                "first_name": "UpdatedName",
                "last_name": "UpdatedLastName",
                "email": "updateduser@example.com",
            },
        )

        # Check that the profile was updated successfully
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedName")
        self.assertEqual(self.user.email, "updateduser@example.com")

        # Check for success message and redirect
        self.assertRedirects(response, reverse("store:dash-board"))
        messages = list(
            get_messages(response.wsgi_request)
        )  # Use get_messages for message assertions
        self.assertEqual(
            str(messages[0]), "Your profile has been updated successfully!"
        )

    def test_dashboard_post_change_password_authenticated(self):
        # Log the user in
        self.client.login(username="testuser", password="testpassword")

        # Simulate a POST request to change the password for authenticated user
        response = self.client.post(
            reverse("store:dash-board"),
            {
                "change_password": "true",
                "old_password": "testpassword",
                "new_password1": "newtestpassword",
                "new_password2": "newtestpassword",
            },
        )

        # Check that the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newtestpassword"))

        # Check for success message and redirect
        self.assertRedirects(response, reverse("store:dash-board"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "Your password has been changed successfully!"
        )

    def test_dashboard_post_update_address_authenticated(self):
        # Log the user in
        self.client.login(username="testuser", password="testpassword")

        # Simulate a POST request to update the address for authenticated user
        response = self.client.post(
            reverse("store:dash-board"),
            {
                "update_address": "true",
                "street_address": "456 New Address",
                "city": "New City",
            },
        )

        # Check that the address was updated successfully
        self.address.refresh_from_db()
        self.assertEqual(self.address.street_address, "456 New Address")
        self.assertEqual(self.address.city, "New City")

        # Check for success message and redirect
        self.assertRedirects(response, reverse("store:dash-board"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "Your address has been updated successfully!"
        )

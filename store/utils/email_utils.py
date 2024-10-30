from django.core.mail import send_mail
from django.conf import settings


def configure_email_settings(
    host, port, username, password, use_tls=True, use_ssl=False
):
    settings.EMAIL_HOST = host
    settings.EMAIL_PORT = port
    settings.EMAIL_HOST_USER = username
    settings.EMAIL_HOST_PASSWORD = password
    settings.EMAIL_USE_TLS = use_tls
    settings.EMAIL_USE_SSL = use_ssl


def send_signup_email(user):
    configure_email_settings(
        host="smtp.signupserver.com",
        port=587,
        username="signup@yourdomain.com",
        password="signup_password",
    )
    send_mail(
        "Welcome to Our Platform",
        "Thank you for signing up!",
        settings.EMAIL_HOST_USER,
        [user.email],
    )


def send_order_confirmation(order):
    configure_email_settings(
        host="smtp.orderserver.com",
        port=587,
        username="orders@yourdomain.com",
        password="order_password",
    )
    send_mail(
        f"Order Confirmation #{order.id}",
        "Thank you for your order!",
        settings.EMAIL_HOST_USER,
        [order.user.email],
    )


def send_promo_email(user, promotion):
    configure_email_settings(
        host="smtp.promoserver.com",
        port=587,
        username="promotions@yourdomain.com",
        password="promo_password",
    )
    send_mail(
        f"Exclusive Offer: {promotion.title}",
        f"Hello {user.first_name}, check out this offer!",
        settings.EMAIL_HOST_USER,
        [user.email],
    )

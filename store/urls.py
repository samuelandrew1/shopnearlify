from django.urls import path
from .views import *
from . import cart_function

# from .order_view import OrderFilterView

app_name = "store"

urlpatterns = [
    # path('admin/book_store/order/report/', order_report_view, name='order_report'),
    path("submit_rating/<str:slug>", product_detail, name="submit_rating"),
    path("email-subscibe", EmailSubscriptionView.as_view(), name="subscribe_email"),
    path("send-newsletter/", send_newsletter, name="send_newsletter"),
    path("product/category/", ProductCategories_view, name="categories-list"),
    path(
        "product/category/<slug:slug>",
        product_list_by_category,
        name="product_list_by_category",
    ),
    #
    path("", home_view, name="index"),
    path("signup/", register, name="signup"),
    path("login", login, name="login"),
    path("update-cart-size/", update_cart_color_and_qty, name="update_cart_size"),
    # cart section
    path("cart-count/", cart_count_view, name="cart-count"),
    #  path('add-to-cart/',add_to_cart, name='add-to-cart'),
    #  path('add-to-cart/',AddToCartView.as_view(), name='add-to-cart'),
    path("delete-from-cart/", delete_cart, name="delete-from-cart"),
    path("update-cart/", UpdateCartQuantity.as_view(), name="update_cart_quantity"),
    path("cart/", CartView.as_view(), name="cart"),
    #  path('cart/<slug>', CartView.as_view(), name='cart_item'),
    path("delete-cart-item/", delete_cart, name="delete-cart-item"),
    # checkout' s
    path("cart/proceed-to-checkout", CheckoutView.as_view(), name="check-out"),
    path("account/profile/dash-board", DashBoardView.as_view(), name="dash-board"),
    path("refund-request", RequestRefund.as_view(), name="refund-request"),
    path("verify-address", verify_address_and_pay, name="verify-address"),
    path("address/edit/<int:pk>", Update_addressView, name="update-address"),
    path("apply-coupon/", apply_coupon, name="apply-coupon"),
    path("search/", search_view, name="search"),
    path("product/<slug>", product_detail, name="product-detail"),
    path(
        "order/<int:order_id>/received/",
        mark_order_as_received,
        name="mark-order-received",
    ),
    path("view/next_product/<slug>", next_product, name="next_product"),
    path("contact/", contact_view, name="contact"),
    path("payment/success", success_page, name="success-page"),
    path("add-to-wishlist/<int:product_id>/", toggle_wishlist, name="add-to-wishlist"),
    path(
        "remove-from-wishlist/<int:product_id>/",
        remove_from_wishlist,
        name="remove-from-wishlist",
    ),
    path("wishlist-count/", wishlist_count, name="wishlist-count"),
    path("wishlist/", wishlist, name="wishlist"),
    path("rate/product/<str:slug>", rate_product, name="rate_product"),
    # path('accounts/confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path("load-cities/", load_cities, name="load_cities"),
    path("cancel-order/<int:order_id>/", cancel_order, name="cancel_order"),
    path("continue-order/<int:order_id>/", cancel_order, name="continue_order"),
    path("site/admin/order/send/invoice/", send_invoice, name="send_invoice_to_mail"),
    path("site/admin/order/view", ViewOrders.as_view(), name="view_orders"),
    path(
        "site/admin/order/view/filter/",
        view_filtered_orders.as_view(),
        name="view_filter_orders",
    ),
    path("site/admin/notifications/", notification_view, name="notification_view"),
    path(
        "site/admin/notifications/delete/",
        delete_notification_action,
        name="delete_notification",
    ),
    path(
        "site/admin/order/cancel/<int:order_id>",
        admin_cancel_order.as_view(),
        name="cancel_order",
    ),
]
# Other URL patterns...

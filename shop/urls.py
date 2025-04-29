from django.urls import path
from . import views
from .views import create_payment_intent, my_orders

urlpatterns = [
    # -------------------- General Pages --------------------
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('category/<slug:slug>/', views.Category, name='Category'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('my-orders/', my_orders, name='my_orders'),

    # -------------------- Authentication --------------------
    path('login/', views.custom_login, name='login'),
    path('signup/', views.signup, name='signup'),

    # -------------------- Cart Management --------------------
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:cupcake_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # -------------------- Checkout & Payment --------------------
    path('checkout/', views.checkout, name='checkout'),
    path('create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order-success/', views.order_success, name='order_success'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment-options/', views.payment_options, name='payment_options'),  # Optional
    path('process-payment/', views.process_payment, name='process_payment'),  # Optional

    # -------------------- Order Management --------------------
    path('orders/', views.view_orders, name='view_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # -------------------- Review System --------------------
    path('add-review/<int:cupcake_id>/', views.add_review, name='add_review'),
]
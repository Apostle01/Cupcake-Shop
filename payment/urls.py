from django.urls import path
from payment import views as payment_views

urlpatterns = [
    path('checkout', payment_views.checkout, name='checkout'),
    path('create-checkout-session', views.create_checkout_session, name='create_checkout_session'),
    path('process_order', payment_views.process_order, name='process_order'),
    path('payment_success', payment_views.payment_success, name='payment_success'),
    path('payment_failed', payment_views.payment_failed, name='payment_failed'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('test-email/', views.test_email_view, name='test_email'),
]

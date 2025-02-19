from django.urls import path
from . import views
from .views import custom_login

urlpatterns = [
    path('', views.shop_now, name='shop_now'),  # This sets '/' as the homepage
    path('shop_now/', views.shop_now, name='shop_now'),  # Add this if needed
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'),  
    
    
    # Cart & Checkout URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('payment_options/', views.payment_options, name='payment_options'),
    path('login/', custom_login, name='login'),  
]


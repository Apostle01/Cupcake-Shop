from django.urls import path
from . import views
from .views import custom_login

urlpatterns = [
    path('', views.home, name='home'),  # Ensuring correct view function is called
    path('shop/', views.shop_now, name='shop'),  # Add this if needed
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'), 
    
    
    # Cart & Checkout URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('payment_options/', views.payment_options, name='payment_options'),
    path('login/', custom_login, name='login'),
    path('add_review', views.add_review, name='add_review'),
    path('add-to-cart/<int:cupcake_id>/', views.add_to_cart, name='add_to_cart'),  
]


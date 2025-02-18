from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'),  
    path('shop/', views.shop, name='shop'),
    
    # Cart & Checkout URLs
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('payment_options/', views.payment_options, name='payment_options'),
]


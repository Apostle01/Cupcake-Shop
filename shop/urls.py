from django.urls import path
from . import views
from .views import custom_login

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'),  
    path('shop/', views.shop, name='shop'),
    
    # Cart & Checkout URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:cupcake_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('payment_options/', views.payment_options, name='payment_options'),
    
    # Review URL
    path('add_review/<int:cupcake_id>/', views.add_review, name='add_review'),
    
    # Authentication
    path('login/', custom_login, name='login'),  
]

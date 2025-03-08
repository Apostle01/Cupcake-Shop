from django.urls import path
from . import views  # Import views correctly

urlpatterns = [
    # General pages
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),  
    path('orders/', views.view_orders, name='view_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),  # Add this line

    # Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),  # Fixed duplicate name
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),  # Add this line!
    path('submit_order/', views.submit_order, name='submit_order'),
    path('payment_options/', views.payment_options, name='payment_options'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('signup/', views.signup, name='signup'),
    
    # Reviews
    path('add_review/<int:cupcake_id>/', views.add_review, name='add_review'),  # Fixed missing ID

    # Cart Management
    path('add-to-cart/<int:cupcake_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),  
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Missing remove function
]

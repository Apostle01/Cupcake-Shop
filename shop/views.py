from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cupcake, Cart, CartItem, Order, Category
from .forms import PaymentForm


# ✅ Home Page
def index(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/index.html', {'cupcakes': cupcakes})

# ✅ Add to Cart (Using Database)
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        cupcake_id = request.POST.get('cupcake_id')
        quantity = int(request.POST.get('quantity', 1))
        cupcake = get_object_or_404(Cupcake, id=cupcake_id)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
        
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        messages.success(request, "Item added to your cart!")
        return redirect('view_cart')
    return redirect('shop')

# ✅ View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    total_price = sum(item.cupcake.price * item.quantity for item in items)
    
    return render(request, 'shop/cart.html', {'cart': cart, 'items': items, 'total_price': total_price})

# ✅ Checkout Page
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    if request.method == "POST":
        order = Order.objects.create(user=request.user)
        for item in items:
            order.items.add(item.cupcake)
        cart.items.all().delete()  # Empty cart after order
        messages.success(request, "Order placed successfully!")
        return redirect('payment_options')
    
    return render(request, 'shop/checkout.html', {'cart': cart, 'items': items})

# ✅ Payment Options Page
@login_required
def payment_options(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            delivery_option = form.cleaned_data['delivery_option']
            messages.success(request, f"Payment successful! Delivery option: {delivery_option}")
            return redirect('index')  # Redirect to home page after payment
    else:
        form = PaymentForm()
    
    return render(request, 'shop/payment_options.html', {'form': form})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    cupcakes = category.cupcake_set.all()
    return render(request, 'shop/category.html', {'category': category, 'cupcakes': cupcakes})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def shop(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/shop.html', {'cupcakes': cupcakes})


def submit_order(request):
    if request.method == 'POST':
        cart_items = request.session.get('cart', {})
        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect('view_cart')

        order = Order.objects.create(user=request.user)
        for cupcake_id, quantity in cart_items.items():
            cupcake = get_object_or_404(Cupcake, id=cupcake_id)
            order.items.create(cupcake=cupcake, quantity=quantity)

        request.session['cart'] = {}  # Clear the cart after order placement
        messages.success(request, "Your order has been placed successfully!")
        return redirect('payment_options')

    return redirect('view_cart')

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})


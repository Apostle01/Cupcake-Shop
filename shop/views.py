from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Cupcake, Cart, CartItem, Review, Category, Product, Order
from django.db.models import Avg

# ---------------- Home & Shop Views ----------------

def home(request):
    cupcakes = Cupcake.objects.all()  # Fetch all cupcakes
    return render(request, 'shop/home.html', {'cupcakes': cupcakes})

def shop(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/shop.html', {'cupcakes': cupcakes})

def shop_now(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'shop/shop.html', {'products': products})

# ---------------- Authentication ----------------

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "You have successfully logged in!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have successfully signed up!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})

# ---------------- Cart Management ----------------
def cart(request):
    return render(request, 'shop/cart.html')
@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    # Calculate total price
    total_price = sum(item.cupcake.price * item.quantity for item in items)

    return render(request, "shop/cart.html", {"cart": cart, "items": items, "total_price": total_price})

@login_required
def add_to_cart(request, cupcake_id):
    cupcake = get_object_or_404(Cupcake, id=cupcake_id)
    
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect("login")  # Redirect to login page
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{cupcake.name} added to cart!")
    return redirect("shop")  # Redirect to shop page

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("view_cart")

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully!")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    
    return redirect("view_cart")  # Redirect to cart page

@login_required
def submit_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    if not items:
        messages.error(request, "Your cart is empty. Add items before submitting an order.")
        return redirect("view_cart")
    
    # Simulate order submission (integrate payment processing here)
    cart.items.all().delete()  # Clear cart after submission
    messages.success(request, "Your order has been successfully placed!")

    return redirect("home")  # Redirect to homepage or order confirmation page

# ---------------- Checkout ----------------

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.cupcake.price * item.quantity for item in items)
    
    if request.method == "POST":
        cart.items.all().delete()  # Clear cart after checkout
        messages.success(request, "Order placed successfully!")
        return redirect("home")  # Redirect after checkout
    
    return render(request, "shop/checkout.html", {"cart": cart, "items": items, "total_price": total_price})

@login_required
def process_checkout(request):
    if request.method == "POST":
        # Payment processing logic goes here
        messages.success(request, "Your order has been placed successfully!")
        return redirect("home")  # Redirect to homepage or order confirmation page
    
    messages.error(request, "Invalid request.")
    return redirect("checkout")

# ---------------- Review System ----------------

@login_required
def add_review(request, cupcake_id):
    cupcake = get_object_or_404(Cupcake, id=cupcake_id)
    existing_review = Review.objects.filter(cupcake=cupcake, user=request.user).first()
    
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()
        
        if not (1 <= rating <= 5):
            messages.error(request, "Invalid rating. Choose a value between 1 and 5.")
            return redirect("product_detail", cupcake_id=cupcake.id)
        
        if not comment:
            messages.error(request, "Comment cannot be empty.")
            return redirect("product_detail", cupcake_id=cupcake.id)
        
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            Review.objects.create(cupcake=cupcake, user=request.user, rating=rating, comment=comment)
            messages.success(request, "Review added successfully!")
        
        return redirect("product_detail", cupcake_id=cupcake.id)
    
    return render(request, "shop/add_review.html", {"cupcake": cupcake, "existing_review": existing_review})

# ---------------- Category & Information Pages ----------------

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category.html', {'category': category, 'products': products})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

@login_required
def payment_options(request):
    return render(request, "shop/payment_options.html")

# ---------------- Order Management ----------------

@login_required
def view_orders(request):
    # Fetch orders for the current user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    # Fetch the order for the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})
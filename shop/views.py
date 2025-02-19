from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product

def index(request):
    return render(request, 'shop/index.html')

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category.html', {'category': category, 'products': products})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop/shop.html', {'products': products})

# Cart & Checkout
def view_cart(request):
    return render(request, 'shop/cart.html')

def add_to_cart(request, cupcake_id):
    return render(request, 'shop/add_to_cart.html', {'cupcake_id': cupcake_id})

def remove_from_cart(request, item_id):
    return render(request, 'shop/remove_from_cart.html', {'item_id': item_id})

def update_cart(request, item_id):
    return render(request, 'shop/update_cart.html', {'item_id': item_id})

def checkout(request):
    return render(request, 'shop/checkout.html')

def submit_order(request):
    return render(request, 'shop/submit_order.html')

def payment_options(request):
    return render(request, 'shop/payment_options.html')

# Review
def add_review(request, cupcake_id):
    return render(request, 'shop/add_review.html', {'cupcake_id': cupcake_id})

# Authentication
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

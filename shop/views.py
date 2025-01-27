from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Cupcake, CartItem, Cart
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    cupcakes = Cupcake.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop/index.html', {'cupcakes': cupcakes, 'categories': categories})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    cupcakes = category.cupcakes.all()
    return render(request, 'shop/category.html', {'category': category, 'cupcakes': cupcakes})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def shop(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/shop.html', {'cupcakes': cupcakes})


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        cupcake_id = request.POST.get('cupcake_id')
        quantity = int(request.POST.get('quantity', 1))
        cupcake = get_object_or_404(Cupcake, id=cupcake_id)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the item is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        return redirect('shop')  # Redirect to the shop page
    return redirect('shop')

from django.contrib import messages


def add_to_cart(request):
    if request.method == 'POST':
        cupcake_id = request.POST.get('cupcake_id')
        quantity = int(request.POST.get('quantity', 1))

        # Assuming you have a session-based cart
        cart = request.session.get('cart', {})
        
        # Add or update the cupcake in the cart
        if cupcake_id in cart:
            cart[cupcake_id] += quantity
        else:
            cart[cupcake_id] = quantity
        
        # Save the updated cart to the session
        request.session['cart'] = cart

        # Success message
        messages.success(request, "Item added to your cart!")
    
    return redirect('shop')  



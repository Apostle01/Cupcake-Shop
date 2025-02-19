from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cupcake, Cart, CartItem, Review
from django.db.models import Avg

@login_required
def add_to_cart(request, cupcake_id):
    cupcake = get_object_or_404(Cupcake, id=cupcake_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{cupcake.name} added to cart!")
    return redirect("view_cart")

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
    return redirect("view_cart")

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.cupcake.price * item.quantity for item in items)
    return render(request, "shop/cart.html", {"cart": cart, "items": items, "total_price": total_price})

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

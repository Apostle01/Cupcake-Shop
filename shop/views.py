from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
import json
from .models import Category, Order, OrderItem, Cart, CartItem, Cupcake, Product, Review

stripe.api_key = settings.STRIPE_SECRET_KEY

# -------------------- Home & Shop Views --------------------
def home(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/home.html', {'cupcakes': cupcakes})

def shop(request):
    products = Product.objects.all()
    return render(request, 'shop/shop.html', {'products': products})

def shop_now(request):
    return shop(request)

# -------------------- Authentication --------------------
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

# -------------------- Cart Management --------------------
@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart) if cart else []
    total_price = sum(item.cupcake.price * item.quantity for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, cupcake_id):
    cupcake = get_object_or_404(Cupcake, id=cupcake_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{cupcake.name} added to cart!")
    return redirect("shop")

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

# -------------------- Orders --------------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'order_items': order.items.all()
    })

@login_required
def order_success(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, 'No order specified.')
        return redirect('home')
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')
    return render(request, 'shop/order_success.html', {
        'order': order,
        'order_items': order.items.all()
    })

# -------------------- Payment --------------------
@csrf_exempt
def create_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        amount = data.get('amount')
        delivery_info = data.get('delivery_info', {})

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method=payment_method_id,
            confirm=True,
            metadata={
                'user_id': request.user.id,
                'delivery_address': delivery_info.get('address', ''),
                'city': delivery_info.get('city', ''),
                'postal_code': delivery_info.get('postal_code', ''),
                'country': delivery_info.get('country', ''),
                'store_pickup': str(delivery_info.get('store_pickup', False))
            }
        )

        if intent.status == 'succeeded':
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            order = Order.objects.create(
                user=request.user,
                total_price=amount / 100,
                stripe_payment_intent_id=intent.id,
                delivery_address=delivery_info.get('address'),
                city=delivery_info.get('city'),
                postal_code=delivery_info.get('postal_code'),
                country=delivery_info.get('country'),
                store_pickup=delivery_info.get('store_pickup', False)
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    cupcake=item.cupcake,
                    quantity=item.quantity,
                    price=item.cupcake.price
                )
            cart_items.delete()

            return JsonResponse({'success': True, 'order_id': order.id, 'message': 'Payment successful! Your order has been placed.'})

        return JsonResponse({'success': False, 'error': 'Payment processing failed. Please try again.'})

    except stripe.error.CardError as e:
        return JsonResponse({'success': False, 'error': e.user_message or 'Your card was declined.'})
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Your cart is empty.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart) if cart else []
    total_price = sum(item.cupcake.price * item.quantity for item in cart_items)
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def order_confirmation(request):
    return render(request, 'shop/order_confirmation.html')


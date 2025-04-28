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

@login_required
def process_checkout(request):
    if request.method == 'POST':
        stripe_token = request.POST.get('stripeToken')

        if not stripe_token:
            messages.error(request, 'Something went wrong with the payment. Please try again.')
            return redirect('payment_options')

        try:
            # Get the user's cart
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total_price = sum(item.cupcake.price * item.quantity for item in cart_items)

            if total_price == 0:
                messages.warning(request, 'Your cart is empty. Please add items to checkout.')
                return redirect('view_cart')

            # Create a Stripe charge
            charge = stripe.Charge.create(
                amount=int(total_price * 100),  # Convert to cents
                currency='usd',
                description='Cupcake Shop Purchase',
                source=stripe_token,
                metadata={'user_id': request.user.id}
            )

            # Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                stripe_charge_id=charge.id  # Store the Stripe charge ID
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    cupcake=item.cupcake,
                    quantity=item.quantity,
                    price=item.cupcake.price
                )

            # Clear the cart
            cart_items.delete()

            # Redirect to the order success page with the order ID
            return redirect('order_success', order_id=order.id)

        except stripe.CardError as e:
            messages.error(request, f'Card error: {e.user_message}')
        except stripe.RateLimitError as e:
            messages.error(request, 'Too many requests to Stripe. Please try again in a few minutes.')
        except stripe.InvalidRequestError as e:
            messages.error(request, f'Invalid Stripe request: {e.user_message}')
        except stripe.AuthenticationError as e:
            messages.error(request, 'Stripe authentication failed. Please contact support.')
        except stripe.APIConnectionError as e:
            messages.error(request, 'Network error communicating with Stripe. Please try again.')
        except stripe.StripeError as e:
            messages.error(request, f'Something went wrong with Stripe: {e.user_message}')
        except Cart.DoesNotExist:
            messages.error(request, 'Your cart no longer exists.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

        return redirect('payment_options')  # Redirect back to payment options on error
    else:
        return redirect('view_cart') # Redirect to cart if not a POST request

def order_success(request, order_id):
    """
    View to display the order success message.
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, 'shop/order_success.html', {'order': order, 'order_items': order_items})
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')



@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data['payment_method_id']
            amount = data['amount']
            delivery_info = data.get('delivery_info', {})

            # Create and confirm PaymentIntent
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
                # Get user's cart
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    total_price=amount / 100,  # Convert back to dollars
                    stripe_payment_intent_id=intent.id,
                    delivery_address=delivery_info.get('address'),
                    city=delivery_info.get('city'),
                    postal_code=delivery_info.get('postal_code'),
                    country=delivery_info.get('country'),
                    store_pickup=delivery_info.get('store_pickup', False)
                )
                
                # Create order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        cupcake=item.cupcake,
                        quantity=item.quantity,
                        price=item.cupcake.price
                    )
                
                # Clear the cart
                cart_items.delete()
                
                return JsonResponse({
                    'success': True,
                    'order_id': order.id,
                    'message': 'Payment successful! Your order has been placed.'
                })
            
            return JsonResponse({
                'success': False, 
                'error': 'Payment processing failed. Please try again.'
            })
            
        except stripe.error.CardError as e:
            return JsonResponse({
                'success': False, 
                'error': e.user_message or 'Your card was declined. Please try another payment method.'
            })
        except Cart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Your cart is empty. Please add items before checkout.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e) or 'An unexpected error occurred. Please try again later.'
            })
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method.'
    })

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

# -------------------- Home & Shop Views --------------------
def home(request):
    cupcakes = Cupcake.objects.all()  # Fetch all cupcakes
    return render(request, 'shop/home.html', {'cupcakes': cupcakes})

def shop(request):
    cupcakes = Cupcake.objects.all()
    return render(request, 'shop/shop.html', {'cupcakes': cupcakes})

def shop_now(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'shop/shop.html', {'products': products})

# -------------------- Authentication --------------------
@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            amount = data.get('amount')

            # Create a PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
            )

            if intent.status == 'succeeded':
                # Payment succeeded
                return JsonResponse({'success': True})
            else:
                # Payment requires additional action (e.g., 3D Secure)
                return JsonResponse({'success': False, 'error': 'Payment requires additional action.'})
        except stripe.error.CardError as e:
            # Payment failed
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            # Other errors
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

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
    # Get the cart for the current user
    cart = Cart.objects.filter(user=request.user).first()
    
    if cart:
        # Get all cart items for the user's cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.cupcake.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0

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

# -------------------- Checkout & Payment --------------------
def checkout(request):
    # Get the cart for the current user
    cart = Cart.objects.filter(user=request.user).first()
    
    if cart:
        # Get all cart items for the user's cart
        cart_items = CartItem.objects.filter(cart=cart)
        cart_total = sum(item.cupcake.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        cart_total = 0

    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'cart_total': cart_total})

def process_checkout(request):
    if request.method == 'POST':
        # Fetch cart items for the current user
        cart_items = CartItem.objects.filter(cart__user=request.user)
        cart_total = sum(item.cupcake.price * item.quantity for item in cart_items)

        # Get delivery/pickup details
        delivery_address = request.POST.get('delivery_address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        store_pickup = request.POST.get('store_pickup') == 'on'

        try:
            # Create a Stripe charge
            charge = stripe.Charge.create(
                amount=int(cart_total * 100),  # Convert to cents
                currency='usd',
                description='Cupcake Shop Purchase',
                source=request.POST.get('stripeToken')
            )

            # Create an order
            order = Order.objects.create(
                user=request.user,
                total_price=cart_total,
                delivery_address=delivery_address if not store_pickup else None,
                city=city if not store_pickup else None,
                postal_code=postal_code if not store_pickup else None,
                country=country if not store_pickup else None,
                store_pickup=store_pickup
            )

           
            # Clear the cart after successful payment
            cart_items.delete()

            messages.success(request, 'Payment successful! Your order has been placed.')
            return redirect('order_confirmation')
        except stripe.error.CardError as e:
            # Handle card errors (e.g., insufficient funds, card declined)
            messages.error(request, f'Card error: {e.error.message}')
        except stripe.error.RateLimitError as e:
            # Handle rate limit errors (too many requests)
            messages.error(request, 'Rate limit exceeded. Please try again later.')
        except stripe.error.InvalidRequestError as e:
            # Handle invalid request errors (e.g., invalid parameters)
            messages.error(request, f'Invalid request: {e.error.message}')
        except stripe.error.AuthenticationError as e:
            # Handle authentication errors (e.g., invalid API key)
            messages.error(request, 'Authentication error. Please contact support.')
        except stripe.error.APIConnectionError as e:
            # Handle API connection errors (e.g., network issues)
            messages.error(request, 'Network error. Please check your connection.')
        except stripe.error.StripeError as e:
            # Handle generic Stripe errors
            messages.error(request, f'Payment failed: {e.error.message}')
        except Exception as e:
            # Handle other unexpected errors
            messages.error(request, f'An unexpected error occurred: {str(e)}')

        return redirect('checkout')
    return redirect('checkout')

# -------------------- Review System --------------------
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

# -------------------- Category & Information Pages --------------------
def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/category.html', {'category': category, 'products': products})

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

# -------------------- Order Management --------------------
@login_required
def order_confirmation(request):
    return render(request, "shop/order_confirmation.html")

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})

def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'my_orders.html', {'orders': orders})
    else:
        return redirect('login')  # Redirect to login if user is not authenticated

@login_required
def payment_options(request):
    """
    View to display payment options.
    """
    return render(request, 'shop/payment_options.html')
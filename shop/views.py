from django.shortcuts import render, redirect
# from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
# from store.models import Product, Profile
import datetime

# Import Some Paypal Stuff
from django.urls import reverse
# from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # unique user id for duplictate orders
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# Get the order
		order = Order.objects.get(id=pk)
		# Get the order items
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# Check if true or false
			if status == "true":
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				order.update(shipped=False)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, 'payment/orders.html', {"order":order, "items":items})




	else:
		messages.success(request, "Access Denied")
		return redirect('home')



def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=True, date_shipped=now)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def process_order(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Get Billing Info from the last page
		payment_form = PaymentForm(request.POST or None)
		# Get Shipping Session Data
		my_shipping = request.session.get('my_shipping')

		# Gather Order Info
		full_name = my_shipping['shipping_full_name']
		email = my_shipping['shipping_email']
		# Create Shipping Address from session info
		shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
		amount_paid = totals

		# Create an Order
		if request.user.is_authenticated:
			# logged in
			user = request.user
			# Create Order
			create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]

			# Delete Cart from Database (old_cart field)
			current_user = Profile.objects.filter(user__id=request.user.id)
			# Delete shopping cart in database (old_cart field)
			current_user.update(old_cart="")


			messages.success(request, "Order Placed!")
			return redirect('home')

			

		else:
			# not logged in
			# Create Order
			create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
			create_order.save()

			# Add order items
			
			# Get the order ID
			order_id = create_order.pk
			
			# Get product Info
			for product in cart_products():
				# Get product ID
				product_id = product.id
				# Get product price
				if product.is_sale:
					price = product.sale_price
				else:
					price = product.price

				# Get quantity
				for key,value in quantities().items():
					if int(key) == product.id:
						# Create order item
						create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
						create_order_item.save()

			# Delete our cart
			for key in list(request.session.keys()):
				if key == "session_key":
					# Delete the key
					del request.session[key]



			messages.success(request, "Order Placed!")
			return redirect('home')


	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Create a session with Shipping Info
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Get the host
		host = request.get_host()
		# Create Paypal Form Dictionary
		paypal_dict = {
			'business': settings.PAYPAL_RECEIVER_EMAIL,
			'amount': totals,
			'item_name': 'Book Order',
			'no_shipping': '2',
			'invoice': str(uuid.uuid4()),
			'currency_code': 'USD', # EUR for Euros
			'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
			'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
			'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
		}

		# Create acutal paypal button
		paypal_form = PayPalPaymentsForm(initial=paypal_dict)


		# Check to see if user is logged in
		if request.user.is_authenticated:
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

		else:
			# Not logged in
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})


		
		shipping_form = request.POST
		return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})	
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def checkout(request):
	# Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	if request.user.is_authenticated:
		# Checkout as logged in user
		# Shipping User
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		# Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form })
	else:
		# Checkout as guest
		shipping_form = ShippingForm(request.POST or None)
		return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})

	

def payment_success(request):
	return render(request, "payment/payment_success.html", {})


def payment_failed(request):
	return render(request, "payment/payment_failed.html", {})

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth import login
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# import stripe
# import json
# from .models import Category, Order, OrderItem, Cart, CartItem, Cupcake, Product, Review

# stripe.api_key = settings.STRIPE_SECRET_KEY

# # -------------------- Home & Shop Views --------------------
# def home(request):
#     cupcakes = Cupcake.objects.all()
#     return render(request, 'shop/home.html', {'cupcakes': cupcakes})

# def shop(request):
#     products = Product.objects.all()
#     return render(request, 'shop/shop.html', {'products': products})

# def shop_now(request):
#     return shop(request)

# # -------------------- Authentication --------------------
# def custom_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             login(request, form.get_user())
#             messages.success(request, "You have successfully logged in!")
#             return redirect('home')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'shop/login.html', {'form': form})

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, "You have successfully signed up!")
#             return redirect('home')
#     else:
#         form = UserCreationForm()
#     return render(request, 'shop/signup.html', {'form': form})

# # -------------------- Cart Management --------------------
# @login_required
# def view_cart(request):
#     cart = Cart.objects.filter(user=request.user).first()
#     cart_items = CartItem.objects.filter(cart=cart) if cart else []
#     total_price = sum(item.cupcake.price * item.quantity for item in cart_items)
#     return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# @login_required
# def add_to_cart(request, cupcake_id):
#     cupcake = get_object_or_404(Cupcake, id=cupcake_id)
#     cart, _ = Cart.objects.get_or_create(user=request.user)
#     cart_item, created = CartItem.objects.get_or_create(cart=cart, cupcake=cupcake)
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     messages.success(request, f"{cupcake.name} added to cart!")
#     return redirect("shop")

# @login_required
# def remove_from_cart(request, item_id):
#     cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
#     cart_item.delete()
#     messages.success(request, "Item removed from cart.")
#     return redirect("view_cart")

# @login_required
# def update_cart(request, item_id):
#     cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
#     if request.method == "POST":
#         quantity = int(request.POST.get("quantity", 1))
#         if quantity > 0:
#             cart_item.quantity = quantity
#             cart_item.save()
#             messages.success(request, "Cart updated successfully!")
#         else:
#             cart_item.delete()
#             messages.success(request, "Item removed from cart.")
#     return redirect("view_cart")

# # -------------------- Orders --------------------
# @login_required
# def my_orders(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'shop/my_orders.html', {'orders': orders})

# @login_required
# def order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     return render(request, 'shop/order_detail.html', {
#         'order': order,
#         'order_items': order.items.all()
#     })

# @login_required
# def order_success(request):
#     order_id = request.GET.get('order_id')
#     if not order_id:
#         messages.error(request, 'No order specified.')
#         return redirect('home')
#     try:
#         order = Order.objects.get(id=order_id, user=request.user)
#     except Order.DoesNotExist:
#         messages.error(request, 'Order not found.')
#         return redirect('home')
#     return render(request, 'shop/order_success.html', {
#         'order': order,
#         'order_items': order.items.all()
#     })

# # -------------------- Payment --------------------
# @csrf_exempt
# def create_payment_intent(request):
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid request method.'})

#     try:
#         data = json.loads(request.body)
#         payment_method_id = data.get('payment_method_id')
#         amount = data.get('amount')
#         delivery_info = data.get('delivery_info', {})

#         intent = stripe.PaymentIntent.create(
#             amount=amount,
#             currency='usd',
#             payment_method=payment_method_id,
#             confirm=True,
#             metadata={
#                 'user_id': request.user.id,
#                 'delivery_address': delivery_info.get('address', ''),
#                 'city': delivery_info.get('city', ''),
#                 'postal_code': delivery_info.get('postal_code', ''),
#                 'country': delivery_info.get('country', ''),
#                 'store_pickup': str(delivery_info.get('store_pickup', False))
#             }
#         )

#         if intent.status == 'succeeded':
#             cart = Cart.objects.get(user=request.user)
#             cart_items = CartItem.objects.filter(cart=cart)

#             order = Order.objects.create(
#                 user=request.user,
#                 total_price=amount / 100,
#                 stripe_payment_intent_id=intent.id,
#                 delivery_address=delivery_info.get('address'),
#                 city=delivery_info.get('city'),
#                 postal_code=delivery_info.get('postal_code'),
#                 country=delivery_info.get('country'),
#                 store_pickup=delivery_info.get('store_pickup', False)
#             )

#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     cupcake=item.cupcake,
#                     quantity=item.quantity,
#                     price=item.cupcake.price
#                 )
#             cart_items.delete()

#             return JsonResponse({'success': True, 'order_id': order.id, 'message': 'Payment successful! Your order has been placed.'})

#         return JsonResponse({'success': False, 'error': 'Payment processing failed. Please try again.'})

#     except stripe.error.CardError as e:
#         return JsonResponse({'success': False, 'error': e.user_message or 'Your card was declined.'})
#     except Cart.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Your cart is empty.'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})

# @login_required
# def checkout(request):
#     cart = Cart.objects.filter(user=request.user).first()
#     cart_items = CartItem.objects.filter(cart=cart) if cart else []
#     total_price = sum(item.cupcake.price * item.quantity for item in cart_items)
#     return render(request, 'shop/checkout.html', {
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
#     })

# @login_required
# def order_confirmation(request):
#     return render(request, 'shop/order_confirmation.html')

# def about(request):
#     return render(request, 'shop/about.html')

# def contact(request):
#     return render(request, 'shop/contact.html')

# @login_required
# def process_checkout(request):
#     return render(request, 'shop/checkout.html')

# @login_required
# def payment_options(request):
#     return render(request, 'shop/payment_options.html')

# @login_required
# def process_payment(request):
#     return render(request, 'shop/process_payment.html')

# @login_required
# def view_orders(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'shop/my_orders.html', {'orders': orders})

# @login_required
# def add_review(request, cupcake_id):
#     messages.info(request, "Review system is under construction.")
#     return redirect('shop')

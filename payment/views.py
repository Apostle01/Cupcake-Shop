import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.shortcuts import render
from .utils.email import send_order_confirmation_email
from shop.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

def test_email_view(request):
    send_order_confirmation_email(
        email='test@example.com',
        order_id='ABC123',
        customer_name='Test User'
    )
    return HttpResponse("Test email sent!")

def send_order_confirmation_email(email):
    send_mail(
        subject='Your Cupcake Order Confirmation',
        message='Thank you for your order! We are preparing your cupcakes.',
        from_email='no-reply@cupcakeshop.com',
        recipient_list=[email],
        fail_silently=False,
    )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = 'whsec_XXXXXXXXXXXXXXXX'  # Replace with your webhook secret
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # ✅ Handle event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email')
        print(f"✅ Payment succeeded for: {customer_email}")
        
        # Optional: trigger order creation or email sending
        # send_order_confirmation_email(customer_email)

    return HttpResponse(status=200)

def checkout(request):
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payment/checkout.html', context)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Box of Cupcakes',
                        },
                        'unit_amount': 2000,  # $20.00
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment_success'),
                cancel_url=request.build_absolute_uri('/payment_failed'),
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})

def payment_success(request):
    return render(request, 'payment/payment_success.html')

def payment_failed(request):
    return render(request, 'payment/payment_failed.html')

@csrf_exempt
def process_order(request):
    if request.method == "POST":
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Create a new order
            customer_email = session.get("customer_email")
            amount_total = session.get("amount_total") / 100  # in dollars

            # Save Order to DB (replace with your model)
            order = Order.objects.create(
                email=customer_email,
                amount=amount_total,
                payment_status="paid",
                stripe_session_id=session.get("id"),
            )

            # Send confirmation email
            subject = "Your Cupcake Shop Order"
            message = render_to_string('emails/order_confirmation.html', {
                'order': order,
            })

            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [customer_email],
                html_message=message,
            )

        return HttpResponse(status=200)
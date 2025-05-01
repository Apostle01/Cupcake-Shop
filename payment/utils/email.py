from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now

def send_order_confirmation_email(email, order_id, customer_name='Customer'):
    context = {
        'customer_email': email,
        'order_id': order_id,
        'customer_name': customer_name,
        'current_year': now().year
    }

    subject = 'Your Cupcake Order Confirmation'
    from_email = 'no-reply@yourdomain.com'
    to = [email]

    text_content = f"Thanks for your order, {customer_name}! Your order ID is {order_id}."
    html_content = render_to_string('emails/order_confirmation.html', context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

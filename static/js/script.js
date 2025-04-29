document.getElementById('pay-now-button').addEventListener('click', async function (e) {
    e.preventDefault();

    const stripe = Stripe('{{ STRIPE_PUBLIC_KEY }}'); // Use your Stripe publishable key
    const paymentMethod = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement, // Your Stripe card element
    });

    if (paymentMethod.error) {
        // Display error message
        console.error(paymentMethod.error.message);
        alert('Payment failed: ' + paymentMethod.error.message);
    } else {
        // Send paymentMethod.id to your backend
        const response = await fetch('/create-payment-intent/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}', // Add CSRF token for Django
            },
            body: JSON.stringify({
                payment_method_id: paymentMethod.paymentMethod.id,
                amount: 1000, // Amount in cents (e.g., $10.00)
            }),
        });

        const data = await response.json();

        if (data.success) {
            // Payment succeeded
            alert('Payment successful!');
            window.location.href = '/order-success/'; // Redirect to success page
        } else {
            // Payment failed
            alert('Payment failed: ' + data.error);
        }
    }
});

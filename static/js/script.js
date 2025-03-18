document.addEventListener("DOMContentLoaded", function () {
    console.log("Custom JS Loaded!");

    // Initialize Stripe with your Publishable Key
    const stripe = Stripe('pk_test_51R46dB2fp2LisM0RSnnZ9JGcfdfPdnFxPhLllASiXWpE9RyMCwIaEk4pdYCU2s5QvBsVZqdNK88v7pKCXKhmcyoo00AtA8BvsH');

    // Example: Create a payment form or handle Stripe Elements
    const elements = stripe.elements();
    const cardElement = elements.create('card');
    cardElement.mount('#card-element');

    // Handle form submission
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const { error, paymentMethod } = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
        });

        if (error) {
            console.error(error);
        } else {
            // Send paymentMethod.id to your server for further processing
            console.log(paymentMethod.id);
        }
    });
});
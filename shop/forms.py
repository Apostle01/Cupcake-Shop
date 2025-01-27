from django import forms

class PaymentForm(forms.Form):
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]
    delivery_option = forms.ChoiceField(choices=DELIVERY_CHOICES, widget=forms.RadioSelect)

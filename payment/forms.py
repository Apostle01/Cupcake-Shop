from django import forms
from .models import ShippingAddress

class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'city', 'postal_code', 'country', 'store_pickup']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'store_pickup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentForm(forms.Form):
    payment_method_id = forms.CharField(widget=forms.HiddenInput())

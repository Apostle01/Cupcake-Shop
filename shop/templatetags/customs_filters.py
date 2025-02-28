# templatetags/custom_filters.py
print("Loading custom_filters library...")  # Debugging statement
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiple the value by the argument"""
    return value * arg
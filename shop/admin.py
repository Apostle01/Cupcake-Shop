from django.contrib import admin
from .models import Category, Product, Cupcake, Cart, CartItem, Order, OrderItem, Review

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cupcake)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)


from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name


class Cupcake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="cupcakes"
    )
    image = models.ImageField(upload_to="cupcakes/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username if self.user else 'Guest'}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    cupcake = models.ForeignKey('Cupcake', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'cupcake')  # Ensures no duplicate items

    def __str__(self):
        return f"{self.quantity} x {self.cupcake.name}"

    def total_price(self):
        return self.cupcake.price * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Replace 1 with an existing User ID in your database
    items = models.ManyToManyField('Cupcake', through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cupcake = models.ForeignKey(Cupcake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.cupcake.name}"
    

class Review(models.Model):
    cupcake = models.ForeignKey(Cupcake, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.cupcake.name}"

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    cupcake = models.ForeignKey(Cupcake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.cupcake.name}"


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

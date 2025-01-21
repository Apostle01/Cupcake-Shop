from django.shortcuts import render, get_object_or_404
from .models import Category, Cupcake

def index(request):
    cupcakes = Cupcake.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop/index.html', {'cupcakes': cupcakes, 'categories': categories})

def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    cupcakes = category.cupcakes.all()
    return render(request, 'shop/category.html', {'category': category, 'cupcakes': cupcakes})


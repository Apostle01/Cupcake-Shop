from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('about/', views.about, name='about'),  
    path('contact/', views.contact, name='contact'),  
    path('shop/', views.shop, name='shop'),
    # path('', include('shop.urls')),  # Assuming the shop app handles URLs like about, contact, and shop  
]

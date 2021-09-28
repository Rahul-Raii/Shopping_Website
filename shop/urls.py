from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
path('', views.index, name="ShopHome"),
path('contact/', views.contact, name="contact"),
path('tracker/', views.tracker, name="tracker"),
path('about/', views.about, name="about"),
path("products/<int:myid>/", views.productview, name="productview"),
path('checkout/', views.checkout, name="checkout"),
path('search/', views.search, name="search"),
path('handlerequest/', views.handlerequest, name="HandleRequest"),
]
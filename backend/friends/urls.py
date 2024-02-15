from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('waiting', views.waiting, name='waiting'),
    path('pending', views.pending, name='pending'),
]

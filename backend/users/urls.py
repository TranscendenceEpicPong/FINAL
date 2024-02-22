from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>', views.search, name='search'),
]

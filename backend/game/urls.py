from django.urls import path 
from . import views 

urlpatterns = [
    path('all', views.get),
    path('join', views.join),
]
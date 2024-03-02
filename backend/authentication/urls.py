from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register, name="register"),
    path("login42", views.login42, name="login42"),
    path("login42_callback", views.login42_callback, name="login42_callback"),
    path("42-register/", views.register42, name="42-register"),
]

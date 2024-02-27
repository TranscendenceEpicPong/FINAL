from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register, name="register"),
    path("request-code", views.request_code, name="request-code"),
    path("enable-2fa", views.enable_2fa, name="enable-2fa"),
    path("disable-2fa", views.disable_2fa, name="disable-2fa"),
    path("check-code", views.check_code, name="check-code"),
]

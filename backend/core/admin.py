from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EpicPongUser

class EpicPongUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'token', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

admin.site.register(EpicPongUser, EpicPongUserAdmin)

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from core.models import EpicPongUser
import sys
from core.config import UserConfig

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(
        label=UserConfig.USERNAME.value['label'],
        max_length=UserConfig.USERNAME.value['max_length'],
        min_length=UserConfig.USERNAME.value['min_length'],
        required=True,
        error_messages=UserConfig.USERNAME.value['error_messages']
    )
    avatar = forms.CharField(
        label=UserConfig.AVATAR.value['label'],
        max_length=UserConfig.AVATAR.value['max_length'],
        min_length=UserConfig.AVATAR.value['min_length'],
        required=False,
        error_messages=UserConfig.AVATAR.value['error_messages']
    )
    password = forms.CharField(
        label=UserConfig.PASSWORD.value['label'],
        max_length=UserConfig.PASSWORD.value['max_length'],
        min_length=UserConfig.PASSWORD.value['min_length'],
        required=True,
        error_messages=UserConfig.PASSWORD.value['error_messages']
    )
    confirm_password = forms.CharField(
        label=UserConfig.CONFIRM_PASSWORD.value['label'],
        max_length=UserConfig.CONFIRM_PASSWORD.value['max_length'],
        min_length=UserConfig.CONFIRM_PASSWORD.value['min_length'],
        required=True,
        error_messages=UserConfig.CONFIRM_PASSWORD.value['error_messages']
    )

    class Meta:
        model = EpicPongUser
        fields = ['username', 'avatar', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Les mots de passe ne sont pas identiques"
            )
        return cleaned_data

    def save(self, commit=True):
        if len(self.cleaned_data["avatar"]) == 0:
            del self.cleaned_data["avatar"]
        del self.cleaned_data["confirm_password"]
        user = EpicPongUser.objects.create_user(**self.cleaned_data)
        return user


class UserLoginForm(forms.ModelForm):
    class Meta:
        model = EpicPongUser
        fields = ['username', 'password']

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(
                "identifiant ou mot de passe incorrect"
            )

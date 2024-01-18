from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from core.models import EpicPongUser


class UserRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = EpicPongUser
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()

        try:
            get_user_model().objects.get(Q(
                email=cleaned_data.get('email')
            ) | Q(
                username=cleaned_data.get('username')
            ))
            raise forms.ValidationError('Email or username already in use')
        except ObjectDoesNotExist:
            pass

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Les mots de passe ne sont pas identiques"
            )
        return cleaned_data

    def save(self, commit=True):
        user = EpicPongUser.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"]
        )
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

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from core.models import EpicPongUser
import sys
from core.config import UserConfig
from django.contrib.auth import \
    update_session_auth_hash

class UserUpdateForm(forms.ModelForm):
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
        required=False,
        error_messages=UserConfig.PASSWORD.value['error_messages']
    )
    confirm_password = forms.CharField(
        label=UserConfig.CONFIRM_PASSWORD.value['label'],
        max_length=UserConfig.CONFIRM_PASSWORD.value['max_length'],
        min_length=UserConfig.CONFIRM_PASSWORD.value['min_length'],
        required=False,
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
        if len(cleaned_data.get('password')) > 0:
            if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
                raise forms.ValidationError(
                    "Les mot de passe sont différents"
                )
        return cleaned_data



    def save(self, commit=True):
        del self.cleaned_data["confirm_password"]
        user = EpicPongUser.objects.create_user(**self.cleaned_data)
        return user

    def update(self, commit=True):
        if self.cleaned_data.get('password'):
            self.instance.set_password(self.cleaned_data['password'])
        if self.cleaned_data.get('avatar'):
            self.instance.avatar = self.cleaned_data.get('avatar')
        if self.cleaned_data.get('username'):
            self.instance.username = self.cleaned_data.get('username')
        self.instance.save()
        return self.instance

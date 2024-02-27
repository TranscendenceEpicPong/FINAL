import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from core.default_avatar import DEFAULT_AVATAR
from .status import A2FStatus
import pyotp
from backend.settings import env
import qrcode as QRGenerator
import io
import base64

def random_token():
    return random.random()


class EpicPongUser(AbstractUser):
    token = models.CharField(max_length=128, default=random_token)
    avatar = models.TextField(default=DEFAULT_AVATAR)
    a2f_token = models.CharField(max_length=128, default='')
    a2f_enabled = models.BooleanField(default=False)

    def request_code(self):
        if self.a2f_enabled:
            return A2FStatus.ALREADY_ACTIVATE.value
        self.a2f_token = pyotp.random_base32()
        self.save()
        code = pyotp.TOTP(self.a2f_token).provisioning_uri(self.username, issuer_name=env("APP_NAME"))
        img = QRGenerator.make(code)
        image_buffer = io.BytesIO()
        img.save(image_buffer)
        image_binary = image_buffer.getvalue()

        base64_encoded = base64.b64encode(image_binary).decode("utf-8")
        return {
            "qrcode": f"data:image/png;base64,{base64_encoded}",
            "secret": self.a2f_token
        }

    def activate_2fa(self, code):
        if self.a2f_enabled:
            return A2FStatus.ALREADY_ACTIVATE.value
        if self.check_code(code) == A2FStatus.VALIDATED.value:
            self.a2f_enabled = True
            self.save()
            return A2FStatus.SUCCESS_ACTIVATED.value
        return A2FStatus.WRONG_CODE.value

    def check_code(self, code):
        totp = pyotp.TOTP(self.a2f_token)
        if totp.now() == code:
            return A2FStatus.VALIDATED.value
        return A2FStatus.WRONG_CODE.value

    def deactivate_2fa(self, password):
        if not self.a2f_enabled:
            return A2FStatus.NOT_ACTIVATED.value
        if not self.check_password(password):
            return A2FStatus.WRONG_PASSWORD.value
        self.a2f_enabled = False
        self.save()
        return A2FStatus.SUCCESS_DEACTIVATED.value
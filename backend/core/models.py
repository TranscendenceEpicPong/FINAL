import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from core.default_avatar import DEFAULT_AVATAR


def random_token():
    return random.random()


class EpicPongUser(AbstractUser):
    token = models.CharField(max_length=128, default=random_token)
    avatar = models.TextField(default=DEFAULT_AVATAR)
    status = models.CharField(max_length=128, default="online")
    id42 = models.CharField(default='')
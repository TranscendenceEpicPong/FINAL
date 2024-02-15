from django.db import models
from core.models import EpicPongUser as User

# Create your models here.
class Blocks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_of_user')
    block = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocks_user')
from django.db import models
from core.models import EpicPongUser as User

# Create your models here.
class Chats(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_receiver')
    content = models.CharField(max_length=50, default='')

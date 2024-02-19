from django.db import models
from core.models import EpicPongUser as User
from .status import Status

# Create your models here.
class Game(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_of_user')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_user', null=True)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner_user', null=True)
    status = models.IntegerField(default=Status.WAITING.value)
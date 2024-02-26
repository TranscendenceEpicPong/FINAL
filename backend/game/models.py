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

    def __str__(self):
        return f"{self.player1} vs {self.player2} - {self.status}"
    
    def leave_game(self, user):
        if self.player2 is None:
            self.delete()
            return
        if self.player1 == user:
            self.winner = self.player2
        else:
            self.winner = self.player1
        self.status = Status.FINISHED.value
        self.save()
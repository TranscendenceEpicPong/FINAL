from django.db import models
from core.models import EpicPongUser as User
from .status import Status
from django.db.models import Q
from .config import GameConfig
from datetime import datetime

# Create your models here.
def current_time():
    return datetime.now()

class Game(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_of_user')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_user', null=True)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner_user', null=True)
    status = models.IntegerField(default=Status.WAITING.value)
    created_at = models.DateTimeField(default=current_time)

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

    def player_score(self, player_have_score):
        if player_have_score == self.player1:
            self.score_player1 += 1
        else:
            self.score_player2 += 1
        self.save()

    def get_the_winner(self):
        if self.score_player1 == GameConfig.OBJECTIVE_SCORE.value:
            return self.player1
        elif self.score_player2 == GameConfig.OBJECTIVE_SCORE.value:
            return self.player2
        return None

    def set_winner(self, user):
        self.winner = user
        self.status = Status.FINISHED.value
        self.save()
from django.db import models
from core.models import EpicPongUser as User
from .status import Status
from django.db.models import Q
from .config import GameConfig
from datetime import datetime
from tournament_app.models import Tournament

# Create your models here.
def current_time():
    return datetime.now()

class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    phase = models.CharField(choices=Tournament.Phases, null=True, blank=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_of_user')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponents_user', null=True)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner_user', null=True)
    status = models.IntegerField(default=Status.WAITING.value)
    created_at = models.DateTimeField(default=current_time)

    def __str__(self):
        return f"{self.player1} vs {self.player2} - {self.status}"

    def check_tournament(self):
        if not self.tournament:
            return
        self.tournament.check_next_phase()
    
    def leave_game(self, user, delete=True):
        if self.player2 is None and delete:
            self.delete()
            return
        if self.player1 == user:
            self.winner = self.player2
        else:
            self.winner = self.player1
        self.status = Status.FINISHED.value
        self.save()
        self.check_tournament()

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
        self.check_tournament()

    def get_player_number(self, user):
        if self.player1 == user:
            return 1
        return 2

    def get_player(self, number):
        if number == 1:
            return self.player1
        return self.player2

    def get_winner(self):
        if self.status != Status.FINISHED.value:
            return None
        return self.player1 \
            if self.score_player2 < self.score_player1 \
            else self.player2

    def get_winner_score(self):
        return max([self.score_player1, self.score_player2])

    def get_loser(self):
        if self.status != Status.FINISHED.value:
            return None
        return self.player1 \
            if self.score_player2 > self.score_player1 \
            else self.player2

    def get_tournament(self):
        return self.tournament

    def get_loser_score(self):
        return min([self.score_player1, self.score_player2])

    def get_as_dict(self):
        return {
            'id': self.id,
            'player1': {
                'id': self.player1.id,
                'username': self.player1.username,
                'alias': self.player1.registrationtournament_set.get(
                    tournament=self.tournament
                ).alias,
            },
            'player2': {
                'id': self.player2.id,
                'username': self.player2.username,
                'alias': self.player2.registrationtournament_set.get(
                    tournament=self.tournament
                ).alias,
            },
            'winner': getattr(self.get_winner(), 'username', None),
            'phase': self.phase,
            'state': self.status,
            'score_player1': self.score_player1,
            'score_player2': self.score_player2,
        }
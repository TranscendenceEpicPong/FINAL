from .status import Status
from .models import Game
from django.db.models import Q

class GameService:
    def __init__(self, owner):
        self.__owner = owner

    def find_a_game(self):
        game = Game.objects.filter(player1__isnull=False, player2__isnull=True, status=Status.WAITING.value)\
        .exclude(player1=self.__owner)\
        .first()
        if game is None:
            return self.create_game()
        game.player2 = self.__owner
        game.status = Status.STARTED.value
        game.save()
        return game
    
    def create_game(self):
        game = Game(player1=self.__owner)
        game.save()
        return game
    
    def get_current_game(self):
        return Game.objects.filter(Q(player1=self.__owner) | Q(player2=self.__owner), Q(status=Status.WAITING.value) | Q(status=Status.STARTED.value)).first()
    
    def stop_game(self, game):
        if game is None:
            return None

        if game.player2 is None:
            game.delete()
            return None

        winner = game.player1
        if self.__owner == game.player1:
            winner = game.player2

        game.winner = winner
        game.status = Status.FINISHED.value
        game.save()

        return {
            "id": game.id,
            "status": game.status,
            "winner": game.winner
        }
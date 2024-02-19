from django.shortcuts import render
from django.contrib.auth import get_user, get_user_model
from django.db.models import Q
from django.http import JsonResponse
from .models import Game
from .service import GameService
from .status import Status, StatusJoin
from core.service import CoreService
from django.views.decorators.http import require_http_methods

# Create your views here.

def get(request):
    return JsonResponse({'channel': "hello"})

@require_http_methods("POST")
def join(request):
    core_service = CoreService()
    user = get_user(request)
    game = Game.objects.filter(Q(player1=user) | Q(player2=user)).filter(Q(status=Status.WAITING.value) | Q(status=Status.STARTED.value)).first()
    if game is not None:
        return core_service.get_response(StatusJoin.ALREADY_IN_GAME.value)
    game = Game.objects.create(player1=user)
    status = StatusJoin.GAME_CREATED.value
    status['game_id'] = game.id
    return core_service.get_response(status)
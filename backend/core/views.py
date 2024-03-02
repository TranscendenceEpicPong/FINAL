from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from core.models import EpicPongUser as User
import json
import jwt
from backend.settings import env
from .status import StatusError, StatusSuccess
from .service import UserService
from core.helpers import get_response, get_cookie
from django.contrib.auth import \
    get_user_model, \
    get_user, \
    update_session_auth_hash
import datetime
from blocks.service import BlockService
from .forms import UserUpdateForm
from game.models import Game
from django.db.models import Q
from game.status import Status

@require_GET
def server_info(request):
    response = JsonResponse({
        "hostname": request.get_host(),
        "version": 1,
        "available": True,
    })
    get_token(request)
    return response

@require_http_methods("GET")
def search(request, username):
    owner = request.user

    user = User.objects.filter(username=username).first()
    block_service = BlockService(user)
    if user is None or block_service.is_block(owner):
        return get_response({ "message": "Utilisateur introuvable", "status": 404})
    games = Game.objects.filter(Q(player1=user) | Q(player2=user))
    victory = games.filter(winner=user).count()
    defeat = games.filter(status=Status.FINISHED.value).exclude(winner=user).count()

    matchs = []
    for game in games:
        matchs.append({
            "id": game.id,
            "player1": game.player1.username,
            "player2": game.player2.username if game.player2 is not None else None,
            "score_player1": game.score_player1,
            "score_player2": game.score_player2,
            "winner": game.winner.username if game.winner is not None else None,
            "status": game.status,
            "date": game.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "wins": victory,
        "loses": defeat,
        "games": matchs,
    }, status=200)

@require_http_methods("GET")
def index(request):
    user = get_user(request)
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
    }, status=200)

@require_http_methods("PATCH")
def update(request):
    current_user = get_user(request)
    try:
        body = json.loads(request.body)
    except:
        return get_response(StatusError.BAD_JSON_FORMAT.value)
    
    form = UserUpdateForm(body, instance=request.user)
    if not form.is_valid():
        return get_response({"message": "Saisie incorrect", "status": 400})
    form.save()

    username = form.cleaned_data.get('username')
    avatar = form.cleaned_data.get('avatar')
    password = form.cleaned_data.get('password')
    confirm_password = form.cleaned_data.get('confirm_password')

    if password and confirm_password and len(password) > 0 and password == confirm_password:
        update_session_auth_hash(request, request.user)

    response = JsonResponse({
        "id": request.user.id,
        "username": username,
        "avatar": request.user.avatar,
    }, status=200)

    token = jwt.encode({
        'id': get_user_model().objects.get(username=request.user.username).id,
        'username': request.user.username,
        'email': request.user.email,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response.set_cookie('authorization',
        value=token,
        path='/',
        samesite='Strict')

    return response
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Friends
from core.models import EpicPongUser as User
from .status import Status, StatusAdding, StatusRemoving, StatusRequest
from .service import FriendService
import json
import jwt
from backend.settings import env
from core.service import CoreService

# Create your views here.
@require_http_methods("GET")
def index(request):
    core_service = CoreService()
    authorization = core_service.get_cookie(request, 'authorization')
    owner_id = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256']).get('id')
    owner = User.objects.filter(id=owner_id).first()

    if owner is None:
        return core_service.get_response({ "message": "Votre compte est invalide", "status": 403})

    raw_friends = Friends.objects.filter(user=owner, status=Status.ACCEPTED.value).values()
    friends = []
    for raw_friend in raw_friends:
        user = User.objects.get(id=raw_friend.get("friend_id"))
        friends.append({
            'id': user.id,
            'avatar': user.avatar,
            'username': user.username,
        })

    return JsonResponse(friends, safe=False, status=200)

@require_http_methods("GET")
def waiting(request):
    core = CoreService()
    owner_id = jwt.decode(request.COOKIES.get('authorization'), env('JWT_SECRET'), algorithms=['HS256']).get('id')

    owner = User.objects.filter(id=owner_id).first()
    if owner is None:
        return core.get_response({ "message": "Votre compte est invalide", "status": 403})

    raw_friends = Friends.objects.filter(friend=owner, status=Status.WAITING.value).values()
    friends = []
    for raw_friend in raw_friends:
        user = User.objects.get(id=raw_friend.get("user_id"))
        friends.append({
            'id': user.id,
            'username': user.username,
        })

    return JsonResponse(friends, safe=False, status=200)

@require_http_methods("GET")
def pending(request):
    owner_id = jwt.decode(request.COOKIES.get('authorization'), env('JWT_SECRET'), algorithms=['HS256']).get('id')
    owner = User.objects.filter(id=owner_id).first()
    if owner is None:
        return JsonResponse({ "message": "Votre compte est invalide" }, status=403)

    raw_friends = Friends.objects.filter(user=owner, status=Status.WAITING.value).values()
    friends = []
    for raw_friend in raw_friends:
        user = User.objects.get(id=raw_friend.get("friend_id"))
        friends.append({
            'id': user.id,
            'sender': owner.username,
            'username': user.username,
        })

    return JsonResponse(friends, safe=False, status=200)
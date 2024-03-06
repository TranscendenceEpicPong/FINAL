from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Friends
from core.models import EpicPongUser as User
from .status import Status, StatusAdding, StatusRemoving, StatusRequest
from .service import FriendService
import json
import jwt
from backend.settings import env
from core.helpers import get_response, get_cookie

# Create your views here.
@require_http_methods("GET")
def index(request):
    authorization = get_cookie(request, 'authorization')
    owner_id = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256']).get('id')
    print(owner_id)
    owner = User.objects.filter(id=owner_id).first()

    if owner is None:
        return get_response({ "message": "Votre compte est invalide", "status": 403})

    raw_friends = Friends.objects.filter(user=owner, status=Status.ACCEPTED.value).values()
    friends = []
    for raw_friend in raw_friends:
        user = User.objects.get(id=raw_friend.get("friend_id"))
        friends.append({
            'id': user.id,
            "sender": {
                "username": owner.username,
                "avatar": owner.avatar,
            },
            "receiver": {
                "username": user.username,
                "avatar": user.avatar,
            },
        })

    return JsonResponse(friends, safe=False, status=200)

@require_http_methods("GET")
def waiting(request):
    owner_id = jwt.decode(request.COOKIES.get('authorization'), env('JWT_SECRET'), algorithms=['HS256']).get('id')

    owner = User.objects.filter(id=owner_id).first()
    if owner is None:
        return get_response({ "message": "Votre compte est invalide", "status": 403})

    raw_friends = Friends.objects.filter(friend=owner, status=Status.WAITING.value).values()
    friends = []
    for raw_friend in raw_friends:
        user = User.objects.get(id=raw_friend.get("user_id"))
        friends.append({
            'id': user.id,
            "sender": {
                "username": user.username,
                "avatar": user.avatar,
            },
            "receiver": {
                "username": owner.username,
                "avatar": owner.avatar,
            },
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
            "sender": {
                "username": owner.username,
                "avatar": owner.avatar,
            },
            "receiver": {
                "username": user.username,
                "avatar": user.avatar,
            },
        })

    return JsonResponse(friends, safe=False, status=200)
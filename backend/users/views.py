from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import EpicPongUser as User
import json
import jwt
from backend.settings import env
from core.helpers import get_response, get_cookie

# Create your views here.
@require_http_methods("GET")
def search(request, username):
    authorization = get_cookie(request, 'authorization')
    owner_id = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256']).get('id')
    print(owner_id)
    owner = User.objects.filter(id=owner_id).first()

    if owner is None:
        return get_response({ "message": "Votre compte est invalide", "status": 403})

    user = User.objects.filter(username=username).first()
    if user is None:
        return get_response({ "message": "Utilisateur introuvable", "status": 404})
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "wins": 10,
        "loses": 5,
    }, safe=False, status=200)
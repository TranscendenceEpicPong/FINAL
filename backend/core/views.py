from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from core.models import EpicPongUser as User
from django.contrib.auth import update_session_auth_hash
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

    if owner is None:
        return get_response({ "message": "Votre compte est invalide", "status": 403})

    user = User.objects.filter(username=username).first()
    block_service = BlockService(user)
    if user is None or block_service.is_block(owner):
        return get_response({ "message": "Utilisateur introuvable", "status": 404})
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "wins": 10,
        "loses": 5,
    }, safe=False, status=200)

@require_http_methods("GET")
def index(request):
    user = get_user(request)
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
    }, safe=False, status=200)

@require_http_methods("PATCH")
def update(request):
    current_user = get_user(request)
    try:
        body = json.loads(request.body)
    except:
        return get_response(StatusError.BAD_JSON_FORMAT.value)

    username = body.get("username")
    avatar = body.get("avatar")
    password = body.get("password")
    confirm_password = body.get("confirm_password")

    if not username and not avatar and not password and not confirm_password:
        return get_response(StatusError.NO_DATA.value)

    validation_username = UserService().validate_username(username, current_user.username)
    if validation_username != StatusSuccess.USERNAME_SUCCESS_VALIDATION.value:
        return get_response(validation_username)

    validation_avatar = UserService().validate_avatar(avatar)
    if validation_avatar != StatusSuccess.AVATAR_SUCCESS_VALIDATION.value:
        return get_response(validation_avatar)

    validation_password = UserService().validate_password(password)
    if validation_password != StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value:
        return get_response(validation_password)

    validation_confirm_password = UserService().validate_confirm_password(password, confirm_password)
    if validation_confirm_password != StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value:
        return get_response(validation_confirm_password)

    request.user.username = username
    if avatar and len(avatar) > 0:
        request.user.avatar = avatar

    if password and confirm_password and len(password) > 0 and password == confirm_password:
        request.user.set_password(password)
        update_session_auth_hash(request, request.user)
    request.user.save()
    response = JsonResponse({
        "id": request.user.id,
        "username": request.user.username,
        "avatar": request.user.avatar,
    }, safe=False, status=200)

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
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from core.models import EpicPongUser as User
from django.core.serializers import serialize
from django.contrib.auth import update_session_auth_hash
import json
import jwt
from backend.settings import env
from django.http import QueryDict
from .status import StatusError, StatusSuccess
from core.config import UserConfig
from .service import UserService
from core.helpers import get_response, get_cookie
from django.contrib.auth import \
    authenticate as django_authenticate, \
    login as django_login, \
    logout as django_logout, \
    get_user_model, \
    get_user, \
    update_session_auth_hash
import datetime

# Create your views here.
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
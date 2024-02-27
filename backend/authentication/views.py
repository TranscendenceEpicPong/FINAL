import json
from typing import Tuple, cast
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import datetime
from django.contrib.auth import \
    authenticate as django_authenticate, \
    login as django_login, \
    logout as django_logout, \
    get_user_model
from core.models import EpicPongUser
from .forms import UserRegisterForm, UserLoginForm
import jwt
from backend.settings import env
from core.helpers import get_response
from core.status import A2FStatus


def perform_auth(request, creds) -> Tuple[JsonResponse, EpicPongUser]:
    user = django_authenticate(request,
                               username=creds['username'],
                               password=creds['password'])
    if user is None:
        return JsonResponse({
            "status": "unauthorized",
            "error": "Wrong credentials"
        }, status=401), get_user_model().objects.none

    django_login(request, user)

    user = cast(get_user_model(), user)
    token = jwt.encode({
        'id': get_user_model().objects.get(username=user.username).id,
        'username': user.username,
        'email': user.email,
        "2fa_enabled": user.a2f_enabled,
        "2fa_verified": False,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response = JsonResponse({
        "status": "success",
        "message": "Successfully authenticated"
    })
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response, user


@require_POST
def login(request):
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON", "status": 400})
    form = UserLoginForm(raw_data)
    if not form.is_valid():
        return JsonResponse(form.errors, status=400)
    response, _ = perform_auth(request, form.cleaned_data)
    return response


@require_POST
def register(request):
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse("Invalid JSON", safe=False, status=400)
    form = UserRegisterForm(raw_data)
    if not form.is_valid():
        return JsonResponse(form.errors, status=400)

    form.save()

    response, _ = perform_auth(request, form.cleaned_data)
    return response


@require_POST
@login_required
def logout(request):
    django_logout(request)
    response = JsonResponse({"status": "success", "message": "Successfully logged out !"})
    response.delete_cookie('authorization')
    return response


@require_POST
@login_required
def request_code(request):
    user = cast(EpicPongUser, request.user)
    return JsonResponse(user.request_code())


@require_POST
@login_required
def enable_2fa(request):
    user = cast(EpicPongUser, request.user)
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return get_response({"message": "Invalid JSON", "status": 400}, True)

    activated_2fa =  user.activate_2fa(raw_data['code'])
    if activated_2fa != A2FStatus.SUCCESS_ACTIVATED.value:
        return get_response(activated_2fa, True)

    token = jwt.encode({
        'id': get_user_model().objects.get(username=user.username).id,
        'username': user.username,
        'email': user.email,
        "2fa_enabled": user.a2f_enabled,
        "2fa_verified": activated_2fa == A2FStatus.SUCCESS_ACTIVATED.value,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response = JsonResponse(activated_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response

@require_POST
@login_required
def disable_2fa(request):
    user = cast(EpicPongUser, request.user)
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return get_response({"message": "Invalid JSON", "status": 400}, True)

    disable_2fa =  user.deactivate_2fa(raw_data['code'])
    if disable_2fa != A2FStatus.SUCCESS_DEACTIVATED.value:
        return get_response(disable_2fa, True)

    token = jwt.encode({
        'id': get_user_model().objects.get(username=user.username).id,
        'username': user.username,
        'email': user.email,
        "2fa_enabled": user.a2f_enabled,
        "2fa_verified": disable_2fa == A2FStatus.SUCCESS_DEACTIVATED.value,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response = JsonResponse(disable_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response


@require_POST
@login_required
def check_code(request):
    user = cast(EpicPongUser, request.user)
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return get_response({"message": "Invalid JSON", "status": 400}, True)

    validated_2fa =  user.check_code(raw_data['code'])
    if validated_2fa != A2FStatus.VALIDATED.value:
        return get_response(validated_2fa, True)

    token = jwt.encode({
        'id': get_user_model().objects.get(username=user.username).id,
        'username': user.username,
        'email': user.email,
        "2fa_enabled": user.a2f_enabled,
        "2fa_verified": validated_2fa == A2FStatus.VALIDATED.value,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response = JsonResponse(validated_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response

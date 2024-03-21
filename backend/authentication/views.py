import json
from typing import Tuple, cast
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.crypto import get_random_string
import datetime
from django.contrib.auth import \
    authenticate as django_authenticate, \
    login as django_login, \
    logout as django_logout, \
    get_user_model
from .forms import UserRegisterForm, UserLoginForm
import jwt
from backend.settings import env
import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from core.models import EpicPongUser
from core.helpers import get_response
from core.status import A2FStatus


def create_token(user: EpicPongUser, a2f_verified: bool) -> str:
    return jwt.encode({
        'id': get_user_model().objects.get(username=user.username).id,
        'username': user.username,
        'email': user.email,
        "a2f_enabled": user.a2f_enabled,
        "a2f_verified": a2f_verified,
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))


def perform_auth(request, creds=None, user: EpicPongUser = None) -> Tuple[JsonResponse, EpicPongUser]:
    if creds:
        user = django_authenticate(request,
                                   username=creds['username'],
                                   password=creds['password'])
    if user is None:
        return JsonResponse({
            "status": "unauthorized",
            "message": "Wrong credentials"
        }, status=401), get_user_model().objects.none

    django_login(request, user)

    user = cast(get_user_model(), user)
    token = create_token(user, False)

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
        return JsonResponse({"error": "Invalid JSON", "status": 400}, status=400)
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
def logout(request):
    django_logout(request)
    response = JsonResponse({"status": "success", "message": "Successfully logged out !"})
    response.delete_cookie('authorization')
    return response


def login42(request):
    authorize_url = f"{env('AUTHORIZE_URL')}?client_id={env('CLIENT_ID')}&redirect_uri={env('REDIRECT_URI')}&response_type=code"
    return redirect(authorize_url)


def login42_callback(request):
    # recup code
    code = request.GET.get('code')

    # code contre token
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": env('CLIENT_ID'),
        "client_secret": env('CLIENT_SECRET'),
        "code": code,
        "redirect_uri": env('REDIRECT_URI')
    }
    response = requests.post(env('TOKEN_URL'), data=token_payload)

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to obtain access token"})

    access_token = response.json()['access_token']

    # récup infos user
    user_info_response = requests.get('https://api.intra.42.fr/v2/me',
                                      headers={'Authorization': 'Bearer ' + access_token})

    if user_info_response.status_code != 200:
        return JsonResponse({"error": "Failed to obtain user info from 42 API"})

    user_info = user_info_response.json()
    username_42 = user_info.get('login')
    id42 = f"{user_info.get('id')}"
    photo = user_info.get('image', {}).get('link', '')

    # check si register ou create
    try:
        user = EpicPongUser.objects.get(id42=id42)
    except EpicPongUser.DoesNotExist:
        username = username_42
        if EpicPongUser.objects.filter(username=username).first():
            i = 2
            while EpicPongUser.objects.filter(username=username).exists():
                username = f"{username_42}_{str(i)}"
                i += 1
        user = EpicPongUser.objects.create_user(id42=id42,
                                                username=username,
                                                password=get_random_string(64),
                                                avatar=photo)

    auth_response, user = perform_auth(request, user=user)

    return auth_response


@require_http_methods('GET')
def request_code(request):
    user = cast(EpicPongUser, request.user)
    return get_response({**user.request_code(), "status": 200})


@require_POST
def enable_2fa(request):
    user = cast(EpicPongUser, request.user)
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return get_response({"message": "Invalid JSON", "status": 400})

    activated_2fa = user.activate_2fa(raw_data.get('code'))
    if activated_2fa != A2FStatus.SUCCESS_ACTIVATED.value:
        return get_response(activated_2fa)

    token = create_token(user, activated_2fa == A2FStatus.SUCCESS_ACTIVATED.value)

    response = JsonResponse(activated_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response


@require_POST
def disable_2fa(request):
    user = cast(EpicPongUser, request.user)
    disable_2fa = user.deactivate_2fa()
    if disable_2fa != A2FStatus.SUCCESS_DEACTIVATED.value:
        return get_response(disable_2fa)

    token = create_token(user, disable_2fa == A2FStatus.SUCCESS_DEACTIVATED.value)

    response = JsonResponse(disable_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response


@require_POST
def check_code(request):
    user = cast(EpicPongUser, request.user)
    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return get_response({"message": "Invalid JSON", "status": 400})

    validated_2fa = user.check_code(raw_data.get('code'))
    if validated_2fa != A2FStatus.VALIDATED.value:
        return get_response(validated_2fa)

    token = create_token(user, validated_2fa == A2FStatus.VALIDATED.value)

    response = JsonResponse(validated_2fa)
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        samesite='Strict')

    return response

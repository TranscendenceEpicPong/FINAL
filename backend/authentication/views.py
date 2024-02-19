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
import io
from .status import StatusLoginError, StatusLogin
from core.service import CoreService

def perform_auth(request, creds) -> Tuple[JsonResponse, EpicPongUser]:
    user = django_authenticate(request,
                               username=creds['username'],
                               password=creds['password'])
    if user is None:
        return JsonResponse({
            "status": "unauthorized",
            "error": "Wrong credentials"
        }, status=401), get_user_model().objects.none

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

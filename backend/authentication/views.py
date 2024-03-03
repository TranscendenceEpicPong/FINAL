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
import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from core.models import EpicPongUser




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


# API 42
CLIENT_ID = "u-s4t2ud-ba30256e8d43ec186c62b98c28d1db0a9169d279f7e85d1a4daa5cb986af0b2b"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8000/authentication/42-register/"
AUTHORIZE_URL = "https://api.intra.42.fr/oauth/authorize"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"

def login42(request):
    authorize_url = f"{AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(authorize_url)

def login42_callback(request):
    # recup code
    code = request.GET.get('code')

    # code contre token
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=token_payload)

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to obtain access token"})
    
    access_token = response.json()['access_token']
    
    # récup infos user
    user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + access_token})
    
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
        user = EpicPongUser.objects.create_user(id42=id42, username=username, password=env('PASSWORD_42AUTH'), avatar=photo)

    auth_response, user = perform_auth(request, {'username':user.username, 'password':env('PASSWORD_42AUTH')})
    
    return auth_response
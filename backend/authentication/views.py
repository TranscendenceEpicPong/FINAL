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



def register42(request):
    response = JsonResponse({"status": "success", "message": "Succesfully register with 42 !"})
    return response


# Définir les URL et les informations de l'API 42
CLIENT_ID = "u-s4t2ud-ba30256e8d43ec186c62b98c28d1db0a9169d279f7e85d1a4daa5cb986af0b2b"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-ba30256e8d43ec186c62b98c28d1db0a9169d279f7e85d1a4daa5cb986af0b2b&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthentication%2F42-register%2F&response_type=code"
AUTHORIZE_URL = "https://api.intra.42.fr/oauth/authorize"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"

def login42(request):
    # Construire l'URL d'autorisation
    authorize_url = f"{AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    
    # Rediriger l'utilisateur vers l'URL d'autorisation
    return redirect(authorize_url)

def login42_callback(request):
    # Récupérer le code d'autorisation à partir de la requête GET
    code = request.GET.get('code')

    # Échanger le code contre un jeton d'accès
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=token_payload)

    # Traiter la réponse pour obtenir le jeton d'accès
    if response.status_code == 200:
        access_token = response.json()['access_token']
        # Utilisez access_token pour faire des requêtes à l'API 42 et authentifier l'utilisateur
        # Par exemple, vous pouvez obtenir des informations sur l'utilisateur ici
        return JsonResponse({"access_token": access_token})
    else:
        return JsonResponse({"error": "Failed to obtain access token"})

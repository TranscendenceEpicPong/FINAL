from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import datetime
from django.contrib.auth import authenticate as django_authenticate, login as django_login, get_user_model
from .forms import UserRegisterForm, UserLoginForm
import jwt
from backend.settings import env


def set_token_cookie(request, response, user):
    token = jwt.encode({
        'username': user.username,
        'email': user.email,
        'sessionId': request.session.session_key,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, env('JWT_SECRET'))

    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        httponly=True)


def perform_auth(request, creds):
    user = django_authenticate(request,
                               username=creds['username'],
                               password=creds['password'])
    if user is None:
        return None

    django_login(request, user)

    return user


@require_POST
def login(request):
    form = UserLoginForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors)

    if perform_auth(request, form.cleaned_data) is None:
        return HttpResponse("Wrong credentials", status=401)

    user = form.instance

    response = HttpResponse("Login successfully!")
    set_token_cookie(request, response, user)

    return response


@require_POST
def register(request):
    raw_data = request.POST
    form = UserRegisterForm(raw_data)

    if not form.is_valid():
        return JsonResponse(form.errors)

    user = form.save()

    perform_auth(request, form.cleaned_data)

    response = HttpResponse("Registration successfully!")
    set_token_cookie(request, response, user)

    return response

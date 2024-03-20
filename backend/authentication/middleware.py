import jwt
from django.http import HttpRequest, JsonResponse

from authentication.views import create_token
from backend.settings import env
from django.conf import settings
from core.helpers import get_response as getJsonResponse
from core.models import EpicPongUser
from django.contrib.auth import logout


def CustomAuthenticationMiddleware(get_response):
    def middleware(request: HttpRequest):
        if request.path in settings.UNAUTHENTICATED_REQUESTS or request.path.startswith('/admin'):
            return get_response(request)
        elif not getattr(request, 'user', None) or not request.user.is_authenticated:
            return getJsonResponse({"message": "Non authentifié", "status": 401})

        authorization = request.COOKIES.get('authorization')
        if not authorization:
            return getJsonResponse({"message": "Missing token", "status": 401})

        try:
            token = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256'])
        except jwt.PyJWTError:
            response = getJsonResponse({"message": "Wrong token", "status": 401})
            response.delete_cookie('authorization')
            logout(request)
            return response

        if token.get('a2f_enabled') and not token.get('a2f_verified') and not (
                request.path in settings.UNAUTHENTICATED_2FA_REQUESTS):
            return getJsonResponse({"message": "2FA required", "status": 401})

        response: JsonResponse = get_response(request)
        if request.path != '/authentication/check-code':
            response.set_cookie('authorization',
                            value=create_token(EpicPongUser.objects.filter(username=request.user.username).first(),
                                               token.get('a2f_verified')),
                            path='/',
                            samesite='Strict')

        return response

    return middleware

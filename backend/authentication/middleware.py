import jwt
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest, JsonResponse
from backend.settings import env
from django.conf import settings
from core.helpers import get_response as getJsonResponse

# TODO: Make a real authentication backend and use JWT for auth
#       Either add a verify token in httpOnly with a hash containing personal token + server salt
#       Or make token based authentication using blacklist, token families, refresh etc...

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
            return getJsonResponse({"message": "Wrong token", "status": 401})


        if token.get('a2f_enabled') and not token.get('a2f_verified') and not (request.path in settings.UNAUTHENTICATED_2FA_REQUESTS):
            return getJsonResponse({"message": "2FA required", "status": 401})

        response: JsonResponse = get_response(request)

        return response

    return middleware

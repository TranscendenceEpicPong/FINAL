import jwt
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest, JsonResponse
from backend.settings import env
from django.conf import settings

# TODO: Make a real authentication backend and use JWT for auth
#       Either add a verify token in httpOnly with a hash containing personal token + server salt
#       Or make token based authentication using blacklist, token families, refresh etc...

def CustomAuthenticationMiddleware(get_response):
    def middleware(request: HttpRequest):
        print(f"({request.path}) ({settings.UNAUTHENTICATED_REQUESTS}) ({request.path in settings.UNAUTHENTICATED_REQUESTS})")
        if request.path in settings.UNAUTHENTICATED_REQUESTS or request.path.startswith('/admin'):
            return get_response(request)
        elif not getattr(request, 'user', None) or not request.user.is_authenticated:
            return JsonResponse({"message": "Non authentifié", "status": 401}, status=401)

        authorization = request.COOKIES.get('authorization')
        if not authorization:
            return HttpResponse("Missing token", status=401)
        # sessionId = request.COOKIES.get('sessionid')
        # session_key = request.session.session_key

        try:
            token = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256'])
        except jwt.PyJWTError:
            return HttpResponse("Wrong token", status=401)

        response: HttpResponse = get_response(request)

        return response

    return middleware

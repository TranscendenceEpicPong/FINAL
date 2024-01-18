import jwt
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest
from backend.settings import env
from django.conf import settings

# TODO: Make a real authentication backend and use JWT for auth
#       Either add a verify token in httpOnly with a hash containing personal token + server salt
#       Or make token based authentication using blacklist, token families, refresh etc...

def CustomAuthenticationMiddleware(get_response):
    def middleware(request: HttpRequest):
        if request.path in settings.UNAUTHENTICATED_REQUESTS:
            return get_response(request)
        elif not getattr(request, 'user', None) or not request.user.is_authenticated:
            return HttpResponseForbidden()

        authorization = request.COOKIES.get('authorization')
        if not authorization:
            return HttpResponse("Missing token", status=401)
        # sessionId = request.COOKIES.get('sessionid')
        # session_key = request.session.session_key

        try:
            token = jwt.decode(authorization, env('JWT_SECRET'), algorithms=['HS256'])
        except jwt.PyJWTError:
            return HttpResponse("Wrong token", status=401)

        # if token.get('sessionId') != session_key:
        #     return HttpResponse("Wrong token", status=401)

        response = get_response(request)

        return response

    return middleware
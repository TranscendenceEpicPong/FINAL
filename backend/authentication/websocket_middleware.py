from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from core.models import EpicPongUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from asgiref.sync import  sync_to_async
from django.contrib.sessions.models import Session
import json
import jwt
from backend.settings import env

@database_sync_to_async
def get_user(userId):
    try:
        return EpicPongUser.objects.get(id=userId)
    except EpicPongUser.DoesNotExist:
        return AnonymousUser()

def get_sessionid(scope):
    try:
        session_key = scope['query_string'].decode().split('=')[1]
        return session_key
    except Exception:
        return None

def get_cookie(cookie, name):
    if not cookie:
        return None
    cookie = cookie.decode()
    try:
        token_key = None
        for c in cookie.split(';'):
            if name in c:
                token_key = c.split('=')[1]
                break
        return token_key
    except Exception:
        return None

def decode_token(token):
    try:
        infos_json = jwt.decode(token, env('JWT_SECRET'), algorithms=['HS256'])
        return infos_json
    except Exception:
        return None

class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers'))
        token = get_cookie(headers.get(b'cookie'), 'authorization')
        sessionid = get_cookie(headers.get(b'cookie'), 'sessionid')
        decoded_token = decode_token(token)
        session = await sync_to_async(Session.objects.filter)(session_key=sessionid)
        session = await sync_to_async(session.first)()
        scope['user'] = AnonymousUser()
        if not session:
            return await super().__call__(scope, receive, send)

        user_id = session.get_decoded().get('_auth_user_id')
        if user_id:
            user_id = int(user_id)
        if user_id == decoded_token.get('id'):
            scope['user'] = await get_user(user_id)
        return await super().__call__(scope, receive, send)
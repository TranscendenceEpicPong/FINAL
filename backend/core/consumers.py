import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
import jwt
from backend.settings import env
from core.models import EpicPongUser
from django.db.models import Q
from friends.models import Friends
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

prefix = "core"

def decode_query_string(query_string):
    try:
        infos_json = jwt.decode(query_string, env('JWT_SECRET'), algorithms=['HS256'])
        return infos_json
    except Exception:
        return None

def send_to_friend(user):
    friends = Friends.objects.filter(user=user)
    channel_layer = get_channel_layer()
    for friend in friends:
        async_to_sync(channel_layer.group_send)(
            f"core-{friend.friend.id}",
            {
                'type': 'update_status',
                'status': "in_game",
                'user': {
                    'id': user.id,
                    'username': user.username,
                }
            }
        )

def update_username_for_friends(user, username):
    friends = Friends.objects.filter(Q(user=user) | Q(friend=user))
    channel_layer = get_channel_layer()
    for friend in friends:
        async_to_sync(channel_layer.group_send)(
            f"core-{friend.friend.id}",
            {
                'type': 'update_username',
                "user": {
                    "id": user.id,
                    'username': username,
                }
            }
        )
    async_to_sync(channel_layer.group_send)(
        f"core-{user.id}",
        {
            'type': 'update_username',
            "user": {
                "id": user.id,
                'username': username,
            }
        }
    )

class CoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'] == AnonymousUser():
            self.close()
            return
        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            self.close()
            return
        user = await self.get_user(infos_json['id'])
        if user is None:
            self.close()
            return
        self.room_group_name = f"{prefix}-{user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        user.status = "online"
        await sync_to_async(user.save)()
        await sync_to_async(self.send_to_friends)(user)
        await self.accept()

    async def update_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def update_username(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_alert(self, event):
        await self.send(text_data=json.dumps(event))

    async def get_user(self, userId):
        user = await sync_to_async(EpicPongUser.objects.filter)(id=userId)
        if await sync_to_async(user.count)() == 0:
            return None
        return await sync_to_async(user.first)()

    def send_to_friends(self, user):
        friends = Friends.objects.filter(Q(user=user) | Q(friend=user))
        channel_layer = get_channel_layer()
        for friend in friends:
            async_to_sync(channel_layer.group_send)(
                f"core-{friend.friend.id}",
                {
                    'type': 'update_status',
                    'status': user.status,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                    }
                }
            )

    async def disconnect(self, close_code):
        infos_json = decode_query_string(self.scope['query_string'])
        user = await self.get_user(infos_json['id'])

        if user is None:
            return
        user.status = "offline"
        await sync_to_async(user.save)()
        await sync_to_async(self.send_to_friends)(user)
        await self.channel_layer.group_discard(
            f"{prefix}-{user.id}",
            self.channel_name
        )
        return super().disconnect(close_code)
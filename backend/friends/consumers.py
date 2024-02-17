import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import jwt
from backend.settings import env
from friends.service import FriendService
from core.models import EpicPongUser
from django.contrib.sessions.models import Session
from django.middleware import common
import json

prefix = "friends"

def decode_query_string(query_string):
    try:
        infos_json = jwt.decode(query_string, env('JWT_SECRET'), algorithms=['HS256'])
        return infos_json
    except Exception:
        return None

class FriendConsumer(WebsocketConsumer):
    def connect(self):
        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            self.close()
            return
        self.room_group_name = f"{prefix}-{infos_json['id']}"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def receive(self, text_data):
        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            self.close()
            return

        owner = EpicPongUser.objects.get(id=infos_json['id'])
        service = FriendService(owner)
        name = infos_json['username']
        try:
            text_data_json = json.loads(text_data)
        except Exception:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Données invalides'
            }))
            return
        try:
            user = EpicPongUser.objects.get(username=text_data_json['username'])
        except EpicPongUser.DoesNotExist:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Utilisateur introuvable'
            }))
            return

        if text_data_json['action'] in ['add', 'accept']:
            status = service.add_friend(user)
        elif text_data_json['action'] == 'delete':
            status = service.delete_friend(user)
        else:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Action inconnue'
            }))
            return

        if status['status'] < 200 or status['status'] >= 300:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':status['message'],
                "sender": name,
                "receiver": text_data_json['username']
            }))
            return

        data_to_send = {
            'type':'add_friend',
            'message': status['message'],
            "status": status['status'],
            "sender": {
                "username": owner.username,
                "avatar": owner.avatar,
            },
            "receiver": {
                "username": user.username,
                "avatar": user.avatar,
            },
            "action": text_data_json['action']
        }

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{user.id}",
            data_to_send
        )

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{infos_json['id']}",
            data_to_send
        )

    def add_friend(self, event):
        self.send(text_data=json.dumps(event))

    def disconnect(self, code):
        return super().disconnect(code)
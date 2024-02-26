import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import base64
from urllib.parse import unquote
import jwt
from backend.settings import env
from friends.service import FriendService
from core.models import EpicPongUser
from .models import Chats

prefix = "chats"

def decode_query_string(query_string):
    try:
        infos_json = jwt.decode(query_string, env('JWT_SECRET'), algorithms=['HS256'])
        return infos_json
    except jwt.ExpiredSignatureError:
        return None

class ChatConsumer(WebsocketConsumer):
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
        owner = EpicPongUser.objects.get(id=infos_json['id'])
        friends = FriendService(owner)
        try:
            text_data_json = json.loads(text_data)
        except Exception:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Données invalides'
            }))
            return

        name = infos_json.get('username')
        username = text_data_json.get('username')
        message = text_data_json.get('message')

        if not message or not username:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':"Message ou nom d'utilisateur manquant"
            }))
            return

        try:
            user = EpicPongUser.objects.get(username=username)
        except EpicPongUser.DoesNotExist:
            self.send(text_data=json.dumps({
                'type':'error',
                'sender': name,
                'receiver': username,
                'message':'Utilisateur introuvable'
            }))
            return

        if owner.id == user.id:
            self.send(text_data=json.dumps({
                'type':'error',
                'sender': name,
                'receiver': username,
                'message':"Vous ne pouvez pas vous envoyer de message à vous même"
            }))
            return

        if not friends.is_friend(user.id):
            self.send(text_data=json.dumps({
                'type':'error',
                'sender': name,
                'receiver': username,
                'message': "Vous n'êtes pas amis avec cet utilisateur"
            }))
            return

        data_to_send = {
            'type':'chat_message',
            'content': message,
            "sender": {
                "username": owner.username,
                "avatar": owner.avatar,
            },
            "receiver": {
                "username": user.username,
                "avatar": user.avatar,
            },
        }

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{user.id}",
            data_to_send
        )

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{infos_json['id']}",
            data_to_send
        )

        sender = EpicPongUser.objects.get(id=infos_json['id'])
        receiver = EpicPongUser.objects.get(username=text_data_json.get('username'))

        Chats.objects.create(sender=sender, receiver=receiver, content=message)

    def chat_message(self, event):
        message = event['content']
        sender = event['sender']
        receiver = event['receiver']

        self.send(text_data=json.dumps({
            'content':message,
            'sender': sender,
            'receiver': receiver
        }))

    def disconnect(self, code):
        return super().disconnect(code)

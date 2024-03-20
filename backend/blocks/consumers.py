import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import jwt
from backend.settings import env
from blocks.service import BlockService
from core.models import EpicPongUser
from django.contrib.auth.models import AnonymousUser

prefix = "blocks"

def decode_query_string(query_string):
    try:
        infos_json = jwt.decode(query_string, env('JWT_SECRET'), algorithms=['HS256'])
        return infos_json
    except jwt.ExpiredSignatureError:
        return None

class BlockConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope['user'] == AnonymousUser():
            self.close()
            return
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
        service = BlockService(owner)
        try:
            text_data_json = json.loads(text_data)
        except Exception:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Données invalides'
            }))
            return
        username = text_data_json.get('username')
        try:
            user = EpicPongUser.objects.get(username=username)
        except EpicPongUser.DoesNotExist:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Utilisateur introuvable'
            }))
            return

        if text_data_json['action'] == 'add':
            status = service.add_block(user)
        elif text_data_json['action'] == 'delete':
            status = service.delete_block(user)
        else:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':'Action inconnue'
            }))
            return

        name = infos_json['username']
        if status['status'] < 200 or status['status'] >= 300:
            self.send(text_data=json.dumps({
                'type':'error',
                'message':status['message']
            }))
            return

        data_to_send = {
            'type':'block_message',
            'message': status['message'],
            "status": status['status'],
            "sender": {
                "id": owner.id,
                "username": owner.username,
                "avatar": owner.avatar,
            },
            "receiver": {
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar,
            },
            'action': text_data_json['action']
        }

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{user.id}",
            data_to_send
        )

        async_to_sync(self.channel_layer.group_send)(
            f"{prefix}-{infos_json['id']}",
            data_to_send
        )

    def block_message(self, event):
        event['type'] = 'block'
        self.send(text_data=json.dumps(event))
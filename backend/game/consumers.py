import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from urllib.parse import unquote
import jwt
from backend.settings import env
from .service import GameService
from core.models import EpicPongUser
from .models import Game
from .status import Status
from django.db.models import Q
import asyncio
from .status import StatusRequest
import copy
from django.contrib.auth import get_user_model
import base64

prefix = "game"

def decode_query_string(query_string):
    try:
        infos_json = jwt.decode(query_string, env('JWT_SECRET'), algorithms=['HS256'])
        # infos_json = json.loads(base64.b64decode(unquote(query_string.decode('utf-8')).split('.')[1]).decode('utf-8'))
        print(infos_json)
        return infos_json
    except Exception:
        return None

class GameConsumer(AsyncWebsocketConsumer):
    players = {}
    OBJECTIVE_SCORE = 3
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 10
    BALL_RADIUS = 5
    games = {
        0: {
            "id": 0,
            "player1": {
                "id": 0,
                "username": "",
                "score": 0,
                "x": 20,
                "y": 200,
                "color": 'green'
            },
            "player2": {
                "id": 0,
                "username": "",
                "score": 0,
                "x": 580,
                "y": 200,
                "color": 'green'
            },
            "ball": {
                "x": 300,
                "y": 200,
                "dx": 5,
                "dy": 0,
            },
            "status": -1,
            "winner": 0,
            "player_scored": 0
        }
    }

    async def connect(self):
        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            self.close()
            return

        user = await self.get_user(infos_json['id'])
        if user is None:
            self.close()
            return
        await self.accept()

    async def receive(self, text_data):
        infos_json = decode_query_string(self.scope['query_string'])
        data = json.loads(text_data)
        user = await self.get_user(infos_json['id'])
        if data['action'] == 'join':
            await self.find_game(user)

    async def get_user(self, userId):
        user = await sync_to_async(EpicPongUser.objects.filter)(id=userId)
        if await sync_to_async(user.count)() == 0:
            return None
        return await sync_to_async(user.first)()

    async def find_game(self, user):
        game = await sync_to_async(Game.objects.filter)(player2__isnull=True)
        if await sync_to_async(game.count)() == 0:
            await self.create_game(user)
        else:
            game = await sync_to_async(game.first)()
            await self.join_game(game, 2, user)

    async def create_game(self, user):
        game = await sync_to_async(Game.objects.create)(player1=user)
        await self.send(text_data=json.dumps({
            'action': 'created',
            'gameId': game.id
        }))
        await self.join_game(game, 1, user)

    async def join_game(self, game, player_number, user):
        if player_number == 1:
            game.player1 = user
            game.status = Status.WAITING.value
        else:
            game.player2 = user
            game.status = Status.STARTED.value
        await sync_to_async(game.save)()
        self.players[f"{user.id}"] = f"{game.id}"

        if self.games.get(f"{game.id}") is None:
            self.games[f"{game.id}"] = copy.deepcopy(self.games[0])

        self.games[f"{game.id}"]['id'] = game.id
        self.games[f"{game.id}"][f"player{player_number}"]['id'] = user.id
        self.games[f"{game.id}"][f"player{player_number}"]['username'] = user.username
        self.games[f"{game.id}"]["status"] = game.status

        self.room_group_name = f"{prefix}-{game.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_infos",
                "action": "joined",
                "game": self.games[f"{game.id}"]
            }
        )

        if player_number == 2:
            asyncio.create_task(self.game_loop({
                "game": self.games[f"{game.id}"]
            }))

    async def game_infos(self, event):
        await self.send(text_data=json.dumps(event))

    async def leave_game(self, game, user):
        if game.player2 is None:
            await sync_to_async(game.delete)()
            return

        if game.player1 == user:
            game.winner = game.player2
        else:
            game.winner = game.player1
        game.status = Status.FINISHED.value
        await sync_to_async(game.save)()

    async def disconnect(self, close_code):
        infos_json = decode_query_string(self.scope['query_string'])
        user = await self.get_user(infos_json['id'])
        if user is None:
            return
        game = await sync_to_async(Game.objects.filter)(Q(player1=user) | Q(player2=user), Q(status=Status.WAITING.value) | Q(status=Status.STARTED.value))
        if await sync_to_async(game.count)() == 0:
            return
        game = await sync_to_async(game.first)()
        if game is not None:
            await sync_to_async(game.leave_game)(user)
        else:
            return
        game_id = self.players.get(f"{user.id}")
        await self.channel_layer.group_discard(
            f"{prefix}-{game_id}",
            self.channel_name
        )
        self.players.pop(f"{user.id}")
        self.games.pop(f"{game_id}")
        return super().disconnect(close_code)

    async def game_loop(self, event):
        game = event['game']
        game_id = game['id']
        while self.games.get(f"{game_id}") is not None and self.games[f"{game_id}"]["status"] != Status.FINISHED.value:
            if game['status'] == Status.STARTED.value:
                self.games[f"{game_id}"] = game
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_infos",
                        "action": "updated",
                        "game": self.games[f"{game_id}"]
                    }
                )
                await asyncio.sleep(0.05)
                self.games[f"{game_id}"]["ball"]["x"] += self.games[f"{game_id}"]["ball"]["dx"]
                if self.games[f"{game_id}"]["ball"]["x"] + self.BALL_RADIUS > self.games[f"{game_id}"]["player2"]["x"] - self.PADDLE_WIDTH:
                    if self.games[f"{game_id}"]["ball"]["y"] > self.games[f"{game_id}"]["player2"]["y"] - (self.PADDLE_HEIGHT / 2) and self.games[f"{game_id}"]["ball"]["y"] < self.games[f"{game_id}"]["player2"]["y"] + (self.PADDLE_HEIGHT / 2):
                        self.games[f"{game_id}"]["ball"]["dx"] *= -1
                elif self.games[f"{game_id}"]["ball"]["x"] - self.BALL_RADIUS < self.games[f"{game_id}"]["player1"]["x"] + self.PADDLE_WIDTH:
                    if self.games[f"{game_id}"]["ball"]["y"] > self.games[f"{game_id}"]["player1"]["y"] - (self.PADDLE_HEIGHT / 2) and self.games[f"{game_id}"]["ball"]["y"] < self.games[f"{game_id}"]["player1"]["y"] + (self.PADDLE_HEIGHT / 2):
                        self.games[f"{game_id}"]["ball"]["dx"] *= -1
            elif game['status'] == Status.FINISHED.value:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_infos",
                        "action": "finished",
                        "game": self.games[f"{game_id}"]
                    }
                )
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                self.players.pop(f"{game['player1']['id']}")
                self.players.pop(f"{game['player2']['id']}")
                self.games.pop(f"{game_id}")

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
    games = {
        0: {
            "player1": {
                "id": 0,
                "username": "",
                "score": 0,
                "startX": 20,
                "startY": 150,
                "endX": 20,
                "endY": 250,
                "color": 'green'
            },
            "player2": {
                "id": 0,
                "username": "",
                "score": 0,
                "startX": 580,
                "startY": 150,
                "endX": 580,
                "endY": 250,
                "color": 'green'
            },
            "ball": {
                "x": 300,
                "y": 200,
                "dx": 5,
                "dy": 5,
            },
            "status": -1,
            "winner": 0,
            "player_scored": 0
        }
    }

    async def connect(self):
        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            print("infos_json is None")
            self.close()
            return

        user = await sync_to_async(EpicPongUser.objects.filter)(id=infos_json['id'])
        if await sync_to_async(user.count)() == 0:
            return self.close()
        user = await sync_to_async(user.first)()

        if self.players.get(infos_json['id']) is not None:
            print("User already connected")
            self.close()
            return

        service = GameService(user)
        game = await sync_to_async(service.find_a_game)()

        self.players[f"{infos_json['id']}"] = f"{game.id}"
        self.room_group_name = f"{prefix}-{game.id}"

        self.create_or_join_game(game, infos_json)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        if game.player2 is None:
            await self.send(text_data=json.dumps({
                "type": "game_status",
                "message": f"Partie créée ({game.id})",
                "status": game.status,
            }))
        else:
            await self.send(text_data=json.dumps({
                "type": "game_status",
                "message": f"Partie rejointe ({game.id})",
                "status": game.status,
            }))
        
        if game.status == Status.STARTED.value:
            await self.channel_layer.group_send(
                f"{prefix}-{self.players.get(infos_json['id'])}",
                {
                    "type": "game_status",
                    "message": "Le jeu peut commencer",
                    "status": game.status,
                }
            )

            asyncio.create_task(self.ball(self.players[f"{infos_json['id']}"]))

    def create_or_join_game(self, game, user):
        if self.games.get(f"{game.id}") is None:
            self.games[f"{game.id}"] = copy.deepcopy(self.games[0])
            self.games[f"{game.id}"]["player1"]["id"] = user['id']
            self.games[f"{game.id}"]["player1"]["username"] = user['username']
            self.games[f"{game.id}"]["status"] = game.status
        else:
            self.games[f"{game.id}"]["player2"]["id"] = user['id']
            self.games[f"{game.id}"]["player2"]["username"] = user['username']
            self.games[f"{game.id}"]["status"] = game.status

    async def receive(self, text_data):
        infos_json = decode_query_string(self.scope['query_string'])
        owner = await sync_to_async(get_user_model().objects.get)(id=infos_json['id'])
        text_data_json = json.loads(text_data)
        game_id = self.players[f"{owner.id}"]

        player = self.games[f"{game_id}"]["player1"]
        if player['id'] != infos_json['id']:
            player = self.games[f"{game_id}"]["player2"]

        if text_data_json['direction'] in ['ArrowUp', 'w'] and player['startY'] > 60:
            player['startY'] -= 10
            player['endY'] -= 10

        if text_data_json['direction'] in ['ArrowDown', 's'] and player['endY'] < 340:
            player['startY'] += 10
            player['endY'] += 10

        await self.channel_layer.group_send(
            f"{prefix}-{game_id}",
            {
                'type': 'game_status',
                'status': 'update_padel',
                'player1': self.games[f"{game_id}"]['player1'],
                'player2': self.games[f"{game_id}"]['player2'],
            }
        )

    async def ball(self, game_id):
        while self.games.get(f"{game_id}") and self.games[f"{game_id}"]['status'] == Status.STARTED.value:
            await self.channel_layer.group_send(
                    f"{prefix}-{game_id}",
                    {
                        'type': 'game_status',
                        'status': 'update_ball',
                        'position': self.games[f"{game_id}"]['ball'],
                        "score": {
                            "player": self.games[f"{game_id}"]['player_scored'],
                            "player1": {
                                "id": self.games[f"{game_id}"]['player1']['id'],
                                "username": self.games[f"{game_id}"]['player1']['username'],
                                "score": self.games[f"{game_id}"]['player1']['score'],
                            },
                            "player2": {
                                "id": self.games[f"{game_id}"]['player2']['id'],
                                "username": self.games[f"{game_id}"]['player2']['username'],
                                "score": self.games[f"{game_id}"]['player2']['score'],
                            }
                        },
                    }
                )
            self.update_ball(game_id)
            await asyncio.sleep(0.1)
        await self.channel_layer.group_send(
            f"{prefix}-{game_id}",
            {
                'type': 'game_status',
                'status': 'game_end',
                'winner': self.games[f"{game_id}"]['winner'],
                "score": {
                    "player": self.games[f"{game_id}"]['player_scored'],
                    "player1": {
                        "id": self.games[f"{game_id}"]['player1']['id'],
                        "username": self.games[f"{game_id}"]['player1']['username'],
                        "score": self.games[f"{game_id}"]['player1']['score'],
                    },
                    "player2": {
                        "id": self.games[f"{game_id}"]['player2']['id'],
                        "username": self.games[f"{game_id}"]['player2']['username'],
                        "score": self.games[f"{game_id}"]['player2']['score'],
                    }
                },
            }
        )
        game = self.games[f"{game_id}"]
        game_db = await sync_to_async(Game.objects.get)(id=game_id)
        game_db.score_player1 = game["player1"]["score"]
        game_db.score_player2 = game["player2"]["score"]
        if game['winner'] == game["player1"]["id"]:
            game_db.winner = await sync_to_async(get_user_model().objects.get)(id=game["player1"]["id"])
        else:
            game_db.winner = await sync_to_async(get_user_model().objects.get)(id=game["player2"]["id"])
        await sync_to_async(game_db.save)()
        self.close()

    def update_ball(self, game_id):
        game = self.games.get(f"{game_id}")
        game['player_scored'] = 0
        if game['ball']['x'] + game['ball']['dx'] >= game['player2']['startX'] - 20:
            if game['ball']['y'] < game['player2']['endY'] and game['ball']['y'] > game['player2']['startY']:
                game['ball']['dx'] = -game['ball']['dx']
            else:
                game['player_scored'] = game['player1']['id']
                game['ball'] = copy.deepcopy(self.games[0]['ball'])
                game['player1']['score'] += 1
                if game['player1']['score'] == self.OBJECTIVE_SCORE:
                    game['status'] = Status.FINISHED
                    game['winner'] = game['player1']['id']

        if game['ball']['x'] + game['ball']['dx'] <= game['player1']['startX'] + 20:
            if game['ball']['y'] < game['player1']['endY'] and game['ball']['y'] > game['player1']['startY']:
                game['ball']['dx'] = -game['ball']['dx']
            else:
                game['player_scored'] = game['player2']['id']
                game['ball'] = copy.deepcopy(self.games[0]['ball'])
                game['player2']['score'] += 1
                if game['player2']['score'] == self.OBJECTIVE_SCORE:
                    game['status'] = Status.FINISHED
                    game['winner'] = game['player2']['id']

        if game['player_scored'] == 0:
            if game['ball']['y'] + 15 >= 400 or game['ball']['y'] - 15 <= 0:
                game['ball']['dy'] = -game['ball']['dy']
            else:
                game['ball']['dy'] = game['ball']['dy']
            
            game['ball']['x'] += game['ball']['dx']
            game['ball']['y'] += game['ball']['dy']
        self.games[f"{game_id}"]['ball'] = game['ball']

    async def game_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def disconnect(self, code):
        if code == 1006:
            return super().disconnect(code)

        infos_json = decode_query_string(self.scope['query_string'])
        if infos_json is None:
            return super().disconnect(code)
        owner = await sync_to_async(get_user_model().objects.get)(id=infos_json['id'])
        service = GameService(owner)
        game = await sync_to_async(service.get_current_game)()
        stopped_game = await sync_to_async(service.stop_game)(game)

        if stopped_game is None:
            await self.channel_layer.group_discard(
                f"{prefix}-{self.players[f"{infos_json['id']}"]}",
                self.channel_name
            )

            return super().disconnect(code)

        await self.channel_layer.group_send(
            f"{prefix}-{self.players[f"{infos_json['id']}"]}",
            {
                "type": "game_status",
                "message": "Le jeu est terminé",
                "status": stopped_game.get('status')
            }
        )

        if stopped_game is not None:
            await self.channel_layer.group_send(
                f"{prefix}-{self.players[f"{infos_json['id']}"]}",
                {
                    "type": "game_status",
                    "message": f"Vainqueur: {stopped_game.get('winner').username}",
                    "status": stopped_game.get('status')
                }
            )

        await self.channel_layer.group_discard(
            f"{prefix}-{self.players[f"{infos_json['id']}"]}",
            self.channel_name
        )

        del self.players[f"{infos_json['id']}"]
        del self.games[f"{stopped_game.get('id')}"]

        return super().disconnect(code)
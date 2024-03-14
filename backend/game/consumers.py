import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
import jwt
from backend.settings import env
from core.models import EpicPongUser
from .models import Game
from .status import Status
from django.db.models import Q
import asyncio
import copy
import random
from .config import GameConfig
from .utils import get_paddle_bottom, get_paddle_top
from channels.layers import get_channel_layer
from friends.models import Friends
from tournament_app.models import Tournament
from django.contrib.auth.models import AnonymousUser

prefix = "game"

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
                'status': user.status,
                'user': {
                    'id': user.id,
                    'username': user.username,
                }
            }
        )

class GameConsumer(AsyncWebsocketConsumer):
    players = {}
    tasks = {}
    games = {
        0: copy.deepcopy(GameConfig.DEFAULT_GAME.value)
    }

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
        await self.accept()

    async def receive(self, text_data):
        infos_json = decode_query_string(self.scope['query_string'])
        data = json.loads(text_data)
        user = await self.get_user(infos_json['id'])
        if data.get('action') == 'join':
            await self.find_game(user)
        elif data.get('action') == 'join-tournament-game':
            await self.join_tournament_game(data, user)
        elif data.get('action') == 'invite':
            await self.invite_friend(data, user)
        elif data.get('action') == 'move':
            await self.move_paddle(data, user)

    async def not_found_user(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Utilisateur non trouvé."
        }))
        return

    async def not_found_game(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Partie non trouvé."
        }))
        return

    async def not_found_tournament(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Tournois non trouvé."
        }))
        return

    async def not_friend(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Vous n'êtes pas amis."
        }))
        return

    async def already_in_game(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Vous êtes déjà dans une partie."
        }))
        return

    async def in_tournament(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Vous êtes déjà dans un tournoi."
        }))
        return

    async def already_invited(self):
        await self.send(text_data=json.dumps({
            'type': 'error',
            "message": "Ami déjà invité."
        }))
        return

    async def join_tournament_game(self, data, user):
        invited_user = await self.get_user_by_username(data.get('username'))
        if invited_user is None:
            return await self.not_found_user()
        tournament = await sync_to_async(Tournament.objects.filter)(id=data.get('tournamentId'))
        if await sync_to_async(tournament.count)() == 0:
            return await self.not_found_tournament()
        tournament = await sync_to_async(tournament.first)()
        game = await sync_to_async(Game.objects.filter)(Q(player1=user, player2=invited_user) | Q(player1=invited_user, player2=user), Q(status=Status.WAITING.value) | Q(status=Status.RESERVED.value), tournament=tournament)
        if await sync_to_async(game.count)() == 0:
            return await self.not_found_game()
        game = await sync_to_async(game.first)()
        if game.status == Status.WAITING.value:
            game.status = Status.RESERVED.value
            if game.player2 == user:
                tmp_player = game.player1
                game.player1 = user
                game.player2 = tmp_player
        elif game.player2 == user:
            game.status = Status.STARTED.value
        else:
            return await self.already_in_game()
        await sync_to_async(game.save)()
        self.players[f"{user.id}"] = f"{game.id}"
        if self.games.get(f"{game.id}") is None:
            self.games[f"{game.id}"] = copy.deepcopy(self.games[0])
        self.games[f"{game.id}"]['id'] = game.id
        self.games[f"{game.id}"]["status"] = game.status
        self.games[f"{game.id}"][f"player{await sync_to_async(game.get_player_number)(user)}"]['id'] = user.id
        self.games[f"{game.id}"][f"player{await sync_to_async(game.get_player_number)(user)}"]['username'] = user.username
        self.room_group_name = f"{prefix}-{game.id}"
        await get_channel_layer().group_add(
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
        if game.status == Status.STARTED.value:
            task = asyncio.create_task(self.game_loop({
                "game": self.games[f"{game.id}"]
            }))
            self.tasks[f"{game.id}"] = task

    async def invite_friend(self, data, user):
        invited_user = await self.get_user_by_username(data.get('username'))
        if invited_user is None:
            return await self.not_found_user()

        friend = await sync_to_async(Friends.objects.filter)(user=user, friend=invited_user)
        if await sync_to_async(friend.count)() == 0:
            return await self.not_friend()

        game = await sync_to_async(Game.objects.filter)(Q(player1=user) | Q(player2=user), Q(status=Status.WAITING.value) | Q(status=Status.STARTED.value))
        if await sync_to_async(game.count)() > 0:
            return await self.already_in_game()
        
        game = await sync_to_async(Game.objects.filter)(Q(player1=user, player2=invited_user), status=Status.RESERVED.value)
        if await sync_to_async(game.count)() > 0:
            return await self.already_invited()

        game = await sync_to_async(Game.objects.filter)(player1=user, status=Status.RESERVED.value)
        if await sync_to_async(game.count)() > 0:
            game = await sync_to_async(game.first)()
            if await sync_to_async(game.get_tournament)() is None:
                await sync_to_async(game.delete)()
            else:
                return await self.in_tournament()

        game = await sync_to_async(Game.objects.filter)(Q(player1=invited_user, player2=user), status=Status.RESERVED.value, tournament__isnull=True)
        if await sync_to_async(game.count)() > 0:
            game = await sync_to_async(game.first)()
            await self.join_game(game, 2, user)
            data_to_send = {
                'type':'chat_message',
                'content': "[start-game]",
                "action": "start-game",
                "sender": {
                    "username": user.username,
                    "avatar": user.avatar,
                },
                "receiver": {
                    "username": invited_user.username,
                    "avatar": invited_user.avatar,
                },
            }

            await get_channel_layer().group_send(
                f"chats-{user.id}",
                data_to_send
            )

            await get_channel_layer().group_send(
                f"chats-{invited_user.id}",
                data_to_send
            )
            return

        game = await sync_to_async(Game.objects.create)(player1=user, player2=invited_user, status=Status.RESERVED.value)
        self.players[f"{user.id}"] = f"{game.id}"

        if self.games.get(f"{game.id}") is None:
            self.games[f"{game.id}"] = copy.deepcopy(self.games[0])

        if self.games.get(f"{game.id}"):
            self.games[f"{game.id}"]['id'] = game.id
            self.games[f"{game.id}"][f"player1"]['id'] = user.id
            self.games[f"{game.id}"][f"player1"]['username'] = user.username
            self.games[f"{game.id}"]["status"] = game.status

        self.room_group_name = f"{prefix}-{game.id}"
        await get_channel_layer().group_add(
            self.room_group_name,
            self.channel_name
        )

        data_to_send = {
            'type':'chat_message',
            'content': "[join-game]",
            "sender": {
                "username": user.username,
                "avatar": user.avatar,
            },
            "receiver": {
                "username": invited_user.username,
                "avatar": invited_user.avatar,
            },
        }

        await get_channel_layer().group_send(
            f"chats-{user.id}",
            data_to_send
        )

        await get_channel_layer().group_send(
            f"chats-{invited_user.id}",
            data_to_send
        )

    async def get_user_by_username(self, username):
        user = await sync_to_async(EpicPongUser.objects.filter)(username=username)
        if await sync_to_async(user.count)() == 0:
            return None
        return await sync_to_async(user.first)()

    async def move_paddle(self, data, user):
        game_id = self.players.get(f"{user.id}")
        if game_id is None:
            return
        game = self.games.get(f"{game_id}")
        if game is None:
            return
        if game.get('status') != Status.STARTED.value:
            return

        player = game["player1"]
        if game['player1']['id'] != user.id:
            player = game['player2']

        if data.get('direction') == 'up' and get_paddle_top(player['y'], GameConfig.PADDLE_HEIGHT.value) > 5:
            player['y'] -= GameConfig.PADDLE_SPEED.value
        if data.get('direction') == 'down' and get_paddle_bottom(player['y'], GameConfig.PADDLE_HEIGHT.value) < 395:
            player['y'] += GameConfig.PADDLE_SPEED.value

        self.games[f"{game_id}"] = game
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_infos",
                "action": "updated",
                "game": self.games[f"{game_id}"]
            }
        )

    async def update_user_status(self, userId, status):
        user = await self.get_user(userId)
        user.status = status
        await sync_to_async(user.save)()
        await sync_to_async(send_to_friend)(user)

    async def get_user(self, userId):
        user = await sync_to_async(EpicPongUser.objects.filter)(id=userId)
        if await sync_to_async(user.count)() == 0:
            return None
        return await sync_to_async(user.first)()

    async def find_game(self, user):
        game = await sync_to_async(Game.objects.filter)(Q(player1=user) | Q(player2=user), Q(status=Status.WAITING.value) | Q(status=Status.STARTED.value))
        if await sync_to_async(game.count)() > 0:
            return await self.already_in_game()

        game = await sync_to_async(Game.objects.filter)(Q(player1=user) | Q(player2=user), Q(status=Status.WAITING.value) | Q(status=Status.RESERVED.value), tournament__isnull=False)
        if await sync_to_async(game.count)() > 0:
            return await self.in_tournament()

        game = await sync_to_async(Game.objects.filter)(player1=user, status=Status.RESERVED.value)
        if await sync_to_async(game.count)() > 0:
            await sync_to_async(game.delete)()

        game = await sync_to_async(Game.objects.filter)(player2__isnull=True, tournament__isnull=True)
        if await sync_to_async(game.count)() == 0:
            await self.create_game(user)
        else:
            game = await sync_to_async(game.first)()
            await self.join_game(game, 2, user)
        await self.update_user_status(user.id, "in_game")

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
            task = asyncio.create_task(self.game_loop({
                "game": self.games[f"{game.id}"]
            }))
            self.tasks[f"{game.id}"] = task

    async def game_infos(self, event):
        await self.send(text_data=json.dumps(event))

    def delete_not_started_games(self, user):
        game = Game.objects.filter(Q(player1=user) | Q(player2=user), Q(status=Status.WAITING.value) | Q(status=Status.RESERVED.value), tournament__isnull=True)
        if game.count() == 0:
            return
        game = game.all()
        for g in game:
            g.delete()

    async def disconnect(self, close_code):
        infos_json = decode_query_string(self.scope['query_string'])
        user = await self.get_user(infos_json['id'])

        if user is None:
            return

        await sync_to_async(self.delete_not_started_games)(user)
        if not close_code:
            await self.update_user_status(user.id, "online")

        game = await sync_to_async(Game.objects.filter)(Q(player1=user) | Q(player2=user), Q(status=Status.STARTED.value) | Q(status=Status.RESERVED.value))
        game = await sync_to_async(game.first)()
        if game is None:
            return

        tournament = await sync_to_async(game.get_tournament)()
        if game.status == Status.STARTED.value:
            await sync_to_async(game.leave_game)(user, tournament is None)
            if self.games.get(f"{game.id}"):
                self.games[f"{game.id}"]['status'] = Status.FINISHED.value
                self.games[f"{game.id}"]['winner'] = game.winner.id
                await self.channel_layer.group_send(
                    f"{prefix}-{game.id}",
                    {
                        "type": "game_infos",
                        "action": "finished",
                        "game": self.games[f"{game.id}"]
                    }
                )
                await self.reset_user(user)
        elif game.status == Status.RESERVED.value:
            if tournament:
                game.status = Status.WAITING.value
                await sync_to_async(game.save)()
            else:
                await sync_to_async(game.delete)()
            await self.reset_user(user)

        ids = {
            f"player1": await sync_to_async(game.get_player)(1),
            f"player2": await sync_to_async(game.get_player)(2),
        }

        player = ids.get('player1')
        if ids.get('player1') == user:
            player = ids.get('player2')
        if player and player.status == "in_game":
            await self.update_user_status(player.id, "online")

        await self.reset_user(player)
        return super().disconnect(close_code)

    async def reset_user(self, user):
        game = self.players.get(f"{user.id}")

        await self.channel_layer.group_discard(
            f"{prefix}-{game}",
            self.channel_name
        )
        if self.players.get(f"{user.id}"):
            self.players.pop(f"{user.id}")
        if self.games.get(f"{game}"):
            self.games.pop(f"{game}")
        if self.tasks.get(f"{game}"):
            self.tasks.get(f"{game}").cancel()

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
                        "game": self.games.get(f"{game_id}")
                    }
                )
                await asyncio.sleep(GameConfig.GAME_SPEED.value)
                await sync_to_async(self.move_ball)(game_id)
                await sync_to_async(self.check_ball_touch_paddle_player1)(game_id)
                await sync_to_async(self.check_ball_touch_paddle_player2)(game_id)
                await sync_to_async(self.check_ball_touch_wall)(game_id)
                current_game = await sync_to_async(Game.objects.get)(id=game_id)
                winner = await sync_to_async(current_game.get_the_winner)()
                if winner is not None:
                    await sync_to_async(current_game.set_winner)(winner)
                    self.games[f"{game_id}"]['status'] = current_game.status
                    self.games[f"{game_id}"]['winner'] = winner.id

        if self.games.get(f"{game_id}") and self.games[f"{game_id}"]['status'] == Status.FINISHED.value:
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
            if self.games.get(f"{game_id}"):
                await self.update_user_status(self.games[f"{game_id}"]["player1"]["id"], "online")
                await self.update_user_status(self.games[f"{game_id}"]["player2"]["id"], "online")
            self.players.pop(f"{game['player1']['id']}")
            self.games.pop(f"{game_id}")
            if self.tasks.get(f"{game_id}"):
                self.tasks.get(f"{game_id}").cancel()
                self.tasks.pop(f"{game_id}")

    def move_ball(self, game_id):
        self.games[f"{game_id}"]["ball"]["x"] += self.games[f"{game_id}"]["ball"]["dx"]
        self.games[f"{game_id}"]["ball"]["y"] += self.games[f"{game_id}"]["ball"]["dy"]

    def check_ball_touch_paddle_player1(self, game_id):
        if self.games[f"{game_id}"]["ball"]["x"] - GameConfig.BALL_RADIUS.value < self.games[f"{game_id}"]["player1"]["x"] + GameConfig.PADDLE_WIDTH.value:
            if self.games[f"{game_id}"]["ball"]["y"] > get_paddle_top(self.games[f"{game_id}"]["player1"]["y"], GameConfig.PADDLE_HEIGHT.value) and self.games[f"{game_id}"]["ball"]["y"] < get_paddle_bottom(self.games[f"{game_id}"]["player1"]["y"], GameConfig.PADDLE_HEIGHT.value):
                self.games[f"{game_id}"]["ball"]["dx"] *= -1
                ball_y = self.games[f"{game_id}"]["ball"]["y"]
                player_y = self.games[f"{game_id}"]["player1"]["y"]
                top_player_y = get_paddle_top(player_y, GameConfig.PADDLE_HEIGHT.value / 2)
                bottom_player_y = get_paddle_bottom(player_y, GameConfig.PADDLE_HEIGHT.value / 2)
                if ball_y < player_y:
                    diff_player_ball = ball_y - player_y
                    diff_player_top = player_y - top_player_y
                    self.games[f"{game_id}"]["ball"]["dy"] = (diff_player_ball / diff_player_top) * 2 * self.games[f"{game_id}"]["ball"]["dx"]
                    self.games[f"{game_id}"]["ball"]["dy"] *= 1
                elif ball_y > player_y:
                    diff_player_ball = ball_y - player_y
                    diff_player_bottom = player_y - bottom_player_y
                    self.games[f"{game_id}"]["ball"]["dy"] = (diff_player_ball / diff_player_bottom) * 2 * self.games[f"{game_id}"]["ball"]["dx"]
                    self.games[f"{game_id}"]["ball"]["dy"] *= -1
                else:
                    self.games[f"{game_id}"]["ball"]["dy"] *= 0
            else:
                self.games[f"{game_id}"]["player2"]["score"] += 1
                self.games[f"{game_id}"]["player_scored"] = self.games[f"{game_id}"]["player2"]["id"]
                game = Game.objects.get(id=game_id)
                game.player_score(game.player2)
                self.reset_by_score(game_id)

    def check_ball_touch_paddle_player2(self, game_id):
        if self.games[f"{game_id}"]["ball"]["x"] + GameConfig.BALL_RADIUS.value > self.games[f"{game_id}"]["player2"]["x"] - GameConfig.BALL_RADIUS.value:
            if self.games[f"{game_id}"]["ball"]["y"] > self.games[f"{game_id}"]["player2"]["y"] - (GameConfig.PADDLE_HEIGHT.value / 2) and self.games[f"{game_id}"]["ball"]["y"] < self.games[f"{game_id}"]["player2"]["y"] + (GameConfig.PADDLE_HEIGHT.value / 2):
                self.games[f"{game_id}"]["ball"]["dx"] *= -1
                ball_y = self.games[f"{game_id}"]["ball"]["y"]
                player_y = self.games[f"{game_id}"]["player2"]["y"]
                top_player_y = get_paddle_top(player_y, GameConfig.PADDLE_HEIGHT.value / 2)
                bottom_player_y = get_paddle_bottom(player_y, GameConfig.PADDLE_HEIGHT.value / 2)
                if ball_y < player_y:
                    diff_player_ball = ball_y - player_y
                    diff_player_top = player_y - top_player_y
                    self.games[f"{game_id}"]["ball"]["dy"] = (diff_player_ball / diff_player_top) * 2 * self.games[f"{game_id}"]["ball"]["dx"]
                    self.games[f"{game_id}"]["ball"]["dy"] *= -1
                elif ball_y > player_y:
                    diff_player_ball = ball_y - player_y
                    diff_player_bottom = player_y - bottom_player_y
                    self.games[f"{game_id}"]["ball"]["dy"] = (diff_player_ball / diff_player_bottom) * 2 * self.games[f"{game_id}"]["ball"]["dx"]
                    self.games[f"{game_id}"]["ball"]["dy"] *= 1
                else:
                    self.games[f"{game_id}"]["ball"]["dy"] *= 0
            else:
                self.games[f"{game_id}"]["player1"]["score"] += 1
                self.games[f"{game_id}"]["player_scored"] = self.games[f"{game_id}"]["player1"]["id"]
                game = Game.objects.get(id=game_id)
                game.player_score(game.player1)
                self.reset_by_score(game_id)

    def check_ball_touch_wall(self, game_id):
        if self.games[f"{game_id}"]["ball"]["y"] - GameConfig.BALL_RADIUS.value < 0 or self.games[f"{game_id}"]["ball"]["y"] + GameConfig.BALL_RADIUS.value > 400:
            self.games[f"{game_id}"]["ball"]["dy"] *= -1

    def reset_by_score(self, game_id):
        dx = self.games[f"{game_id}"]["ball"]["dx"]
        self.games[f"{game_id}"]["ball"] = copy.deepcopy(self.games[0]["ball"])
        self.games[f"{game_id}"]["ball"]["dx"] = dx * -1
        self.games[f"{game_id}"]["ball"]["dy"] = random.random() * random.choice([-1, 1]) * self.games[f"{game_id}"]["ball"]["dx"]
        self.games[f"{game_id}"]["player1"]['x'] = copy.deepcopy(self.games[0]["player1"]['x'])
        self.games[f"{game_id}"]["player1"]['y'] = copy.deepcopy(self.games[0]["player1"]['y'])
        self.games[f"{game_id}"]["player2"]['x'] = copy.deepcopy(self.games[0]["player2"]['x'])
        self.games[f"{game_id}"]["player2"]['y'] = copy.deepcopy(self.games[0]["player2"]['y'])
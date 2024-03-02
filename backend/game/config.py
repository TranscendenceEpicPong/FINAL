from enum import Enum

class GameConfig(Enum):
    OBJECTIVE_SCORE = 5
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 10
    BALL_RADIUS = 5
    BALL_SPEED = 5
    PADDLE_SPEED = 5
    GAME_SPEED = 0.017
    DEFAULT_GAME = {
        "id": 0,
        "player1": {
            "id": 0,
            "username": "",
            "score": 0,
            "x": 10,
            "y": 200,
            "color": '#131316'
        },
        "player2": {
            "id": 0,
            "username": "",
            "score": 0,
            "x": 790,
            "y": 200,
            "color": '#131316'
        },
        "ball": {
            "x": 400,
            "y": 200,
            "dx": 5,
            "dy": 0,
        },
        "status": -1,
        "winner": 0,
        "player_scored": 0,
    }
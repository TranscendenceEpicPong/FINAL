from enum import Enum

class Status(Enum):
    WAITING = 0
    STARTED = 1
    FINISHED = 2
    RESERVED = 3

class StatusRequest(Enum):
    BAD_JSON_FORMAT = { "message": "Mauvais format JSON", "status": 400 }

class StatusJoin(Enum):
    ALREADY_IN_GAME = { "message": "Vous n'êtes déjà dans une partie", "status": 409 }
    GAME_CREATED = { "message": "Partie créée, en attente d'autres joueurs...", "game_id": 0, "status": 200 }
    GAME_STARTED = { "message": "La partie commence", "status": 200 }
    GAME_NOT_FOUND = { "message": "Partie non trouvée", "status": 404 }
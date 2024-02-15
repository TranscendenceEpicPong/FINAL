from enum import Enum

class StatusAdding(Enum):
    NOT_FOUND = {"message": "Utilisateur introuvable", "status": 404}
    ADDING_YOURSELF = {"message": "Impossible de se bloqué soi-même", "status": 400}
    ALREADY_BLOCKED = {"message": "Utilisateur déjà bloqué", "status": 409}
    SUCCESS_BLOCKING = {"message": "Utilisateur bloqué", "status": 200}

class StatusRemoving(Enum):
    NOT_FOUND = {"message": "Utilisateur introuvable", "status": 404}
    REMOVING_YOURSELF = {"message": "Impossible de se débloqué soi-même", "status": 400}
    NOT_BLOCKED = {"message": "Utilisateur non bloqué", "status": 404}
    SUCCESS_UNBLOCKING = {"message": "Utilisateur débloqué", "status": 200}
    FAILED_REMOVING = {"message": "Impossible débloqué l'utilisateur", "status": 400}
from enum import Enum

class Status(Enum):
    WAITING = 0
    ACCEPTED = 1

class StatusRequest(Enum):
    BAD_JSON_FORMAT = {"message": "Mauvais format JSON", "status": 400}

class StatusAdding(Enum):
    NOT_FOUND_REQUEST = {"message": "Demande d'ami introuvable", "status": 404}
    NOT_FOUND = {"message": "Utilisateur introuvable", "status": 404}
    ADDING_YOURSELF = {"message": "Impossible de s'ajouter soi-même", "status": 400}
    ADDING_BLOCKED = {"message": "Impossible d'ajouter cet utilisateur", "status": 403}
    BLOCKED_USER = {"message": "Vous avez bloqué cet utilisateur", "status": 403}
    ALREADY_FRIEND = {"message": "Vous êtes déjà ami avec cet utilisateur", "status": 409}
    ALREADY_REQUEST = {"message": "La demande est déjà en attente", "status": 409}
    SUCCESS_REQUEST = {"message": "Demande d'ami envoyée", "status": 200}
    SUCCESS_ACCEPT = {"message": "Demande d'ami acceptée", "status": 200}

class StatusRemoving(Enum):
    NOT_FOUND = {"message": "Utilisateur introuvable", "status": 404}
    REMOVING_YOURSELF = {"message": "Impossible de supprimer soi-même", "status": 400}
    REQUEST_REMOVED={"message": "Demande d'ami supprimée", "status": 200}
    NOT_FRIEND = {"message": "Vous n'êtes pas ami avec cet utilisateur", "status": 404}
    SUCCESS_REMOVING = {"message": "Ami supprimé", "status": 200}
    FAILED_REMOVING = {"message": "Impossible de supprimer l'ami", "status": 400}
    DECLINE_REQUEST = {"message": "Demande d'ami refusée", "status": 200}
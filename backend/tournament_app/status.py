from enum import Enum


class Status(Enum):
    NOT_FOUND = {"message": "Tournois introuvable", "status": 404}
    INVALID_SYNTAXE = {"message": "Syntaxe invalide", "status": 400}


class StatusCreating(Enum):
    EMPTY_ALIAS = {"message": "Un alias est nécessaire", "status": 400}
    BAD_FORMAT_ALIAS = {"message": "L'alias doit être une chaine de caractère", "status": 400}

    EMPTY_NAME = {"message": "Un nom de tournois est nécessaire", "status": 400}
    BAD_FORMAT_NAME = {"message": "Le nom du tournois doit être une chaine de caractère", "status": 400}

    ALREADY_EXIST = {"message": "Le nom est déjà utilisé", "status": 409}
    INVALID_MAX_PARTICIPANTS = {"message": "Le nombre de participants doit être un entier compris entre 3 et 20",
                                "status": 400}
    SUCCESS = {"message": "Création réussie", "status": 201}


class StatusJoin(Enum):
    NOT_FOUND = {"message": "Tournois introuvable", "status": 404}
    EMPTY_ALIAS = {"message": "Un alias est nécessaire", "status": 400}
    EMPTY_TOURNAMENT_NAME = {"message": "Un nom de tournois est nécessaire", "status": 400}
    CLOSED = {"message": "Le tournois est fermé", "status": 403}
    FULL = {"message": "Le tournois est complet", "status": 403}
    ALREADY_REGISTERED = {"message": "Vous êtes déjà inscrit", "status": 409}
    SUCCESS = {"message": "Inscription réussie", "status": 201}


class StatusStart(Enum):
    NOT_FOUND = {"message": "Tournois introuvable", "status": 404}
    ALREADY_STARTED = {"message": "Le tournois a déjà commencé", "status": 409}
    NOT_ENOUGH_PARTICIPANTS = {"message": "Il n'y a pas assez de participants", "status": 409}
    SUCCESS = {"message": "Le tournois commence", "status": 201}


class StatusParticipants(Enum):
    NOT_FOUND = {"message": "Participants introuvables", "status": 404}
    INVALID_ID = {"message": "ID invalide", "status": 400}
    SUCCESS = {"message": "Participants mis à jour", "status": 201}

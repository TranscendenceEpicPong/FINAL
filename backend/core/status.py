from enum import Enum
from core.config import UserConfig

class StatusError(Enum):
    NOT_IDENTICAL_PASSWORDS = { "message": "Les mots de passe ne sont pas identiques", "status": 400 }
    PASSWORD_TOO_SHORT = { "message": f"Le mot de passe est trop court", "status": 400 }
    PASSWORD_TOO_LONG = { "message": f"Le mot de passe est trop long", "status": 400 }
    PASSWORD_INVALID_TYPE = { "message": "Le mot de passe doit être chaîne de caractères", "status": 400 }

    CONFIRM_PASSWORD_TOO_SHORT = { "message": f"La confirmation du mot de passe est trop court", "status": 400 }
    CONFIRM_PASSWORD_TOO_LONG = { "message": f"La confirmation du mot de passe est trop long", "status": 400 }

    USERNAME_ALREADY_TAKEN = { "message": "Le nom d'utilisateur est déjà pris", "status": 400 }
    USERNAME_TOO_SHORT = { "message": f"Le nom d'utilisateur est trop court", "status": 400 }
    USERNAME_TOO_LONG = { "message": f"Le nom d'utilisateur est trop long", "status": 400 }
    USERNAME_INVALID_TYPE = { "message": "Le nom d'utilisateur doit être une chaîne de caractères", "status": 400 }

    AVATAR_TOO_SHORT = { "message": f"L'avatar est trop court", "status": 400 }
    AVATAR_TOO_LONG = { "message": f"L'avatar est trop long", "status": 400 }
    AVATAR_INVALID_TYPE = { "message": "L'avatar doit être chaîne de caractères", "status": 400 }

    BAD_JSON_FORMAT = { "message": "Format JSON invalide", "status": 400 }
    NO_DATA = { "message": "Aucune donnée à mettre à jour", "status": 400 }

    NOT_FOUND_PROFILE = { "message": "Profil introuvable", "status": 404 }

class StatusSuccess(Enum):
    PASSWORD_SUCCESS_VALIDATION = { "message": "Mot de passe validé avec succès", "status": 200 }
    USERNAME_SUCCESS_VALIDATION = { "message": "Nom d'utilisateur validé avec succès", "status": 200 }
    AVATAR_SUCCESS_VALIDATION = { "message": "Avatar validé avec succès", "status": 200 }

    PROFILE_DELETED = { "message": "Profil supprimé", "status": 200 }

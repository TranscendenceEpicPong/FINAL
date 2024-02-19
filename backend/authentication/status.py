from enum import Enum

class Status2FAActivation(Enum):
    WRONG_CODE = {"message": "Code invalide", "status": 403}
    ALREADY_ACTIVATED = {"message": "2FA déjà activé", "status": 409}
    SUCCESS = {"message": "2FA activé", "status": 200}

class Status2FADeactivation(Enum):
    WRONG_PASSWORD = {"message": "Mot de passe incorrect", "status": 403}
    NOT_ACTIVATED = {"message": "2FA non activé", "status": 409}
    SUCCESS = {"message": "2FA désactivé", "status": 200}

class StatusLoginError(Enum):
    WRONG_CREDENTIALS = {"message": "Nom d'utilisateur ou mot de passe invalide", "status": 401}

class StatusLogin(Enum):
    SUCCESS = {"message": "Connexion réussie", "status": 200}
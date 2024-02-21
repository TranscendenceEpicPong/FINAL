from enum import Enum


class UserConfig(Enum):
    USERNAME = {"label": "Nom d'utilisateur", "max_length": 20, "min_length": 3, "error_messages": {
        "required": "Ce champ est obligatoire",
        "max_length": "Le nom d'utilisateur est trop long",
        "min_length": "Le nom d'utilisateur est trop court (Min 3 caractères)"
    }}
    AVATAR = {"label": "Avatar", "max_length": 32000, "min_length": 3, "error_messages": {
        "required": "Ce champ est obligatoire",
        "max_length": "Le lien de l'avatar est trop long",
        "min_length": "Le lien de l'avatar est trop court (Min 3 caractères)"
    }}
    PASSWORD = {"label": "Mot de passe", "max_length": 128, "min_length": 3, "error_messages": {
        "required": "Ce champ est obligatoire",
        "max_length": "Le mot de passe est trop long",
        "min_length": "Le mot de passe est trop court (Min 3 caractères)"
    }}
    CONFIRM_PASSWORD = {"label": "Confirmation du mot de passe", "max_length": 128, "min_length": 3, "error_messages": {
        "required": "Ce champ est obligatoire",
        "max_length": "La confirmationd du mot de passe est trop long",
        "min_length": "La confirmationd du mot de passe est trop court (Min 3 caractères)"
    }}

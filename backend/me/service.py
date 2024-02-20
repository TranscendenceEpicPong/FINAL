from core.config import UserConfig
from .status import StatusError, StatusSuccess
from core.models import EpicPongUser as User

class UserService:
    def __init__(self):
        pass

    def __check_username_type(self, username):
        if type(username) != str:
            return StatusError.USERNAME_INVALID_TYPE.value

        return StatusSuccess.USERNAME_SUCCESS_VALIDATION.value

    def __check_username_length(self, username):
        if len(username) < UserConfig.USERNAME.value['min_length']:
            return StatusError.USERNAME_TOO_SHORT.value

        if len(username) > UserConfig.USERNAME.value['max_length']:
            return StatusError.USERNAME_TOO_LONG.value

        return StatusSuccess.USERNAME_SUCCESS_VALIDATION.value

    def validate_username(self, username, current_username):
        type_state = self.__check_username_type(username)
        if type_state != StatusSuccess.USERNAME_SUCCESS_VALIDATION.value:
            return type_state

        length_state = self.__check_username_length(username)
        if length_state != StatusSuccess.USERNAME_SUCCESS_VALIDATION.value:
            return length_state

        if username != current_username and User.objects.filter(username=username).exists():
            return StatusError.USERNAME_ALREADY_TAKEN.value

        return StatusSuccess.USERNAME_SUCCESS_VALIDATION.value

    def __check_avatar_type(self, avatar):
        if type(avatar) != str:
            return StatusError.AVATAR_INVALID_TYPE.value

        return StatusSuccess.AVATAR_SUCCESS_VALIDATION.value

    def __check_avatar_length(self, avatar):
        if len(avatar) < UserConfig.AVATAR.value['min_length']:
            return StatusError.AVATAR_TOO_SHORT.value

        if len(avatar) > UserConfig.AVATAR.value['max_length']:
            return StatusError.AVATAR_TOO_LONG.value

        return StatusSuccess.AVATAR_SUCCESS_VALIDATION.value

    def validate_avatar(self, avatar):
        validation_state = self.__check_avatar_type(avatar)
        if validation_state == StatusSuccess.AVATAR_SUCCESS_VALIDATION.value:
            return self.__check_avatar_length(avatar)

        return validation_state

    def __check_password_type(self, password):
        if type(password) == str:
            return StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value
        if password is None:
            return StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value
        return StatusError.PASSWORD_INVALID_TYPE.value

    def __check_password_length(self, password):
        if password is None or len(password) == 0:
            return StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value

        if len(password) < UserConfig.PASSWORD.value['min_length']:
            return StatusError.PASSWORD_TOO_SHORT.value

        if len(password) > UserConfig.PASSWORD.value['max_length']:
            return StatusError.PASSWORD_TOO_LONG.value

        return StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value

    def validate_password(self, password):
        validation_state = self.__check_password_type(password)
        if validation_state == StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value:
            return self.__check_password_length(password)

        return validation_state

    def validate_confirm_password(self, password, confirm_password):
        validation_state = self.__check_password_type(confirm_password)
        if validation_state != StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value:
            return StatusError.NOT_IDENTICAL_PASSWORDS.value

        if password != confirm_password:
            return StatusError.NOT_IDENTICAL_PASSWORDS.value

        return StatusSuccess.PASSWORD_SUCCESS_VALIDATION.value
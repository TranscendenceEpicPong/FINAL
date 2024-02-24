from .status import Status, StatusAdding, StatusRemoving
from .models import Friends
from blocks.models import Blocks
from chats.models import Chats

class FriendService:
    def __init__(self, owner):
        self.__owner = owner

    def __has_already_request(self, user):
        try:
            Friends.objects.get(user=self.__owner, friend=user, status=Status.WAITING.value)
            return True
        except Friends.DoesNotExist:
            return False

    def is_friend(self, user):
        try:
            friend = Friends.objects.get(user=self.__owner, friend=user, status=Status.ACCEPTED.value)
            return True
        except Friends.DoesNotExist:
            return False

    def __is_waiting_friend(self, user):
        try:
            friend = Friends.objects.get(user=user, friend=self.__owner, status=Status.WAITING.value)
            return True
        except Friends.DoesNotExist:
            return False

    def __request_waiting(self, user):
        try:
            friend = Friends.objects.get(friend=user, user=self.__owner, status=Status.WAITING.value)
            return True
        except Friends.DoesNotExist:
            return False

    def __accept(self, user):
        friend = None
        try:
            friend = Friends.objects.get(user=user, friend=self.__owner, status=Status.WAITING.value)
        except Friends.DoesNotExist:
            return False
        friend.status = Status.ACCEPTED.value
        friend.save()

        Friends.objects.create(user=self.__owner, friend=user, status=Status.ACCEPTED.value)
        return True

    def __decline(self, user):
        friend = None
        try:
            friend = Friends.objects.get(user=user, friend=self.__owner, status=Status.WAITING.value)
        except Friends.DoesNotExist:
            return False
        friend.delete()
        return True

    def __remove_request(self, user):
        friend = None
        try:
            friend = Friends.objects.get(user=self.__owner, friend=user, status=Status.WAITING.value)
        except Friends.DoesNotExist:
            return False
        friend.delete()
        return True

    def __delete(self, user):
        friend = None
        try:
            friend = Friends.objects.get(user=self.__owner, friend=user, status=Status.ACCEPTED.value)
        except Friends.DoesNotExist:
            return False
        friend.delete()

        try:
            friend = Friends.objects.get(user=user, friend=self.__owner, status=Status.ACCEPTED.value)
        except Friends.DoesNotExist:
            return False
        friend.delete()

        Chats.objects.filter(sender=self.__owner, receiver=user).delete()
        Chats.objects.filter(sender=user, receiver=self.__owner).delete()

        return True

    def add_friend(self, user):
        if user.id == self.__owner.id:
            return StatusAdding.ADDING_YOURSELF.value

        if Blocks.objects.filter(user=self.__owner, block=user).exists():
            return StatusAdding.BLOCKED_USER.value
    
        if Blocks.objects.filter(user=user, block=self.__owner).exists():
            return StatusAdding.ADDING_BLOCKED.value

        if self.__has_already_request(user):
            return StatusAdding.ALREADY_REQUEST.value

        if self.is_friend(user):
            return StatusAdding.ALREADY_FRIEND.value

        if self.__is_waiting_friend(user):
            self.__accept(user)
            return StatusAdding.SUCCESS_ACCEPT.value

        Friends.objects.create(user=self.__owner, friend=user, status=Status.WAITING.value)
        return StatusAdding.SUCCESS_REQUEST.value

    def delete_friend(self, user):
        if user.id == self.__owner.id:
            return StatusRemoving.REMOVING_YOURSELF.value

        if self.__is_waiting_friend(user):
            self.__decline(user)
            return StatusRemoving.DECLINE_REQUEST.value

        if self.__request_waiting(user) == True:
            self.__remove_request(user)
            return StatusRemoving.REQUEST_REMOVED.value

        if self.is_friend(user) == False:
            return StatusRemoving.NOT_FRIEND.value

        if self.__delete(user) == True:
            return StatusRemoving.SUCCESS_REMOVING.value

        return StatusRemoving.NOT_FOUND.value
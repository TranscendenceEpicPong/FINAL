from .status import StatusAdding, StatusRemoving
from .models import Blocks
from friends.models import Friends
from chats.models import Chats

class BlockService:
    def __init__(self, owner):
        self.__owner = owner

    def is_block(self, user):
        return Blocks.objects.filter(user=self.__owner, block=user).exists()

    def __delete(self, user):
        block = None
        try:
            block = Blocks.objects.get(user=self.__owner, block=user)
        except Blocks.DoesNotExist:
            return False
        block.delete()

        return True

    def add_block(self, user):
        if user.id == self.__owner.id:
            return StatusAdding.ADDING_YOURSELF.value

        if self.is_block(user):
            return StatusAdding.ALREADY_BLOCKED.value

        Friends.objects.filter(user=self.__owner, friend=user).delete()
        Friends.objects.filter(user=user, friend=self.__owner).delete()

        Chats.objects.filter(sender=self.__owner, receiver=user).delete()
        Chats.objects.filter(sender=user, receiver=self.__owner).delete()

        Blocks.objects.create(user=self.__owner, block=user)
        return StatusAdding.SUCCESS_BLOCKING.value

    def delete_block(self, user):
        if user.id == self.__owner.id:
            return StatusRemoving.REMOVING_YOURSELF.value

        if self.is_block(user) == False:
            return StatusRemoving.NOT_BLOCKED.value

        if self.__delete(user) == True:
            return StatusRemoving.SUCCESS_UNBLOCKING.value

        return StatusRemoving.NOT_FOUND.value
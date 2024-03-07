from django.core.management.base import BaseCommand

from core.models import EpicPongUser


class Command(BaseCommand):
    help = 'Create random_users'

    def handle(self, *args, **options):
        user_id = EpicPongUser.objects.latest('id').id + 1
        for i in range(user_id, user_id + 20):
            EpicPongUser.objects.create_user(username=f'user-{i}')


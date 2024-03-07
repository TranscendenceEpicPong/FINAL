from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from tournament_app.models import Tournament, RegistrationTournament
class Command(BaseCommand):
    help = 'Create a new tournament'

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, help='ID of the tournament', default=0, nargs='?')

    def handle(self, *args, **options):
        tournament_id = options.get('id', None)
        if tournament_id:
            tournament = Tournament.objects.get(id=tournament_id)
        else:
            tournament = Tournament.objects.latest('id')

        for participant in tournament.participants.all():
            if not participant.alias:
                participant.alias = participant.user.username
            participant.is_active = True
            participant.save()

        # first_user, created = get_user_model().objects.get_or_create(username='user1')
        # if created:
        #     first_user.set_password('')
        #     first_user.save()
        #
        # tournament = Tournament.objects.create(name=name)
        #
        # self.stdout.write(self.style.SUCCESS(f'Tournament "{name}" created successfully.'))
        #
        # for i in range(1, max_participants + 1):
        #     username = f'user{i}'
        #     alias = f'alias_user{i}'
        #
        #     user, created = get_user_model().objects.get_or_create(username=username)
        #
        #     RegistrationTournament.objects.create(user=user, tournament=tournament, alias=alias)
        #
        #     self.stdout.write(self.style.SUCCESS(f'User "{username}" registered with alias "{alias}"'))
        #
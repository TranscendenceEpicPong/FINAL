from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from tournament_app.models import Tournament, RegistrationTournament
class Command(BaseCommand):
    help = 'Register all users for tournament'

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

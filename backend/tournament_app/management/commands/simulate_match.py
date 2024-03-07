#########################################################################################
#                                                                                       #
#   Use :                                                                               #
#          python manage.py simulate_match <tournament_name> <phase>                    #
#                                                                                       #
#   phase option:                                                                       #
#          pool; eighth; quarter; semi; final                                           #
#                                                                                       #
#########################################################################################

from django.core.management.base import BaseCommand
from tournament_app.models import Match, Tournament
import random


class Command(BaseCommand):
    help = 'Simulate matches with random scores in a given phase'

    def add_arguments(self, parser):
        parser.add_argument('id', type=str, help='ID of the tournament', default=0, nargs='?')

    def handle(self, *args, **options):
        id = options['id']

        try:
            tournament = Tournament.objects.get(id=id)
        except Tournament.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tournament "{id}" does not exist.'))
            return

        matches = tournament.current_matches

        for match in matches:
            winner = random.choice([match.player1, match.player2])

            match.score_player1 = 3 if winner == match.player1 else random.randint(0, 2)
            match.score_player2 = 3 if winner == match.player2 else random.randint(0, 2)

            match.state = Match.MATCH_STATE_CHOICES[-1][0]

            match.save()

        if tournament.Phases.POOL_PHASE == tournament.phase:
            tournament.update_tournament_results()
        self.stdout.write(self.style.SUCCESS('Simulation complete.'))

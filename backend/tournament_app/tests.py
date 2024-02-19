import json
import random

from django.contrib.auth import get_user_model
from django.test import TestCase

from tournament_app.models import Tournament, RegistrationTournament
from tournament_app.utils import update_tournament_results


# Create your tests here.
class TournamentsTestCase(TestCase):
    def setUp(self):
        name = "test"
        max_participants = 8

        first_user, created = get_user_model().objects.get_or_create(username='user1')
        if created:
            first_user.set_password('')
            first_user.save()

        self.tournament = Tournament.objects.create(
            name=name,
            max_participants=max_participants,
        )

        for i in range(1, max_participants + 1):
            username = f'user{i}'
            alias = f'alias_user{i}'

            user, created = get_user_model().objects.get_or_create(username=username)

            RegistrationTournament.objects.create(user=user, tournament=self.tournament, alias=alias)

        creds = {
            "username": "john",
            "password": "johnpassword"
        }
        get_user_model().objects.create_user(**creds)

        # This doesn't work because we don't have a real authentication backend
        # self.client.login(**creds)

        self.client.post('/authentication/login', json.dumps(creds), content_type='application/json')

    def test_get_tournament(self):
        response = self.client.get(f"/tournaments/{self.tournament.id}/")
        self.assertEqual(response.status_code, 200)


class PhasesTestCase(TestCase):
    def create_tournament(self, nb_participants):
        tournament = Tournament.objects.create(
            name=f"test_{nb_participants}_participants",
            max_participants=nb_participants,
        )
        for i in range(nb_participants):
            username = f'user{i}'
            alias = f'alias_user{i}'
            user, created = get_user_model().objects.get_or_create(username=username)
            RegistrationTournament.objects.create(user=user, tournament=tournament, alias=alias)
        return tournament

    def start_next_phase(self, tournament: Tournament):
        tournament.update_tournament_results()
        tournament.start_next_phase()

    def assertNextPhase(self, tournament, expected: Tournament.Phases):
        self.start_next_phase(tournament)
        self.assertEqual(tournament.phase, expected)

    def test_tournament_not_started(self):
        tournament = self.create_tournament(3)
        self.assertEqual(tournament.phase, Tournament.Phases.NOT_STARTED)
        self.assertNextPhase(tournament, Tournament.Phases.POOL_PHASE)

    def test_three_participants(self):
        tournament = self.create_tournament(3)
        self.start_next_phase(tournament)
        self.assertNextPhase(tournament, Tournament.Phases.FINAL_PHASE)

    def test_four_participants(self):
        for i in range(4, 8):
            # print(f"Test with {i} participants")
            tournament = self.create_tournament(i)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.SEMI_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.FINAL_PHASE)

    def test_eight_participants(self):
        for i in range(8, 16):
            tournament = self.create_tournament(i)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.QUARTER_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.SEMI_PHASE)

    def test_sixteen_participants(self):
        for i in range(16, 21):
            # print(f"\nTest with {i} participants")
            tournament = self.create_tournament(i)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.EIGHT_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.QUARTER_PHASE)


class ScoreTest(TestCase):
    def setUp(self):
        nb_participants = 8
        self.tournament = Tournament.objects.create(
            name=f"test_score",
            max_participants=nb_participants,
        )
        for i in range(nb_participants):
            username = f'user{i}'
            alias = f'alias_user{i}'
            user, created = get_user_model().objects.get_or_create(username=username)
            RegistrationTournament.objects.create(user=user, tournament=self.tournament, alias=alias)

        self.tournament.start_next_phase()

    def test_random_score(self):
        base_first: RegistrationTournament = self.tournament.ranking.first()
        matches = self.tournament.current_matches
        for index, match in enumerate(matches):
            # print(f"Match #{index}")

            match.score_player1 = 0 \
                if match.player1 == base_first.user \
                else random.randint(0, 5)

            match.score_player2 = 0 \
                if match.player2 == base_first.user \
                else random.randint(0, 5)

            match.save()

        self.tournament.update_tournament_results()
        self.assertNotEqual(base_first, self.tournament.ranking.first())

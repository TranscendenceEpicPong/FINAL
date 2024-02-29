import json
import random
from typing import List

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import EpicPongUser
from tournament_app.models import Tournament, RegistrationTournament
from tournament_app.serializers import TournamentSerializer, ParticipantSerializer
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

    def test_matchmaking(self):
        participants = self.tournament.participants.all()
        for index, participant in enumerate(participants):
            participant.points = index

        self.tournament.start_next_phase()

        match = self.tournament.current_matches[0]
        self.assertEqual(match.player1, participants[0].user)
        self.assertEqual(match.player2, participants[7].user)


class TournamentSerializerTests(TestCase):
    def setUp(self):
        self.num_participants = 8
        self.users: List[EpicPongUser] = [
            get_user_model().objects.create_user({
                "username": f"user{i}"
            }) for i in range(self.num_participants)
        ]

    def test_valid_tournament_data(self):
        serializer = TournamentSerializer(data={
            "name": "Tournament",
            "participants": [{
                "user": user.username,
            } for user in self.users]
        })
        self.assertTrue(serializer.is_valid())

    def test_participant_serializer(self):
        serializer = ParticipantSerializer(data={
            "user": self.users[0].username,
        })
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertEqual(serializer.validated_data["user"], self.users[0])

    def test_create_tournament(self):
        name = "Tournament"
        serializer = TournamentSerializer(data={
            "name": name,
            "participants": [{
                "user": user.username,
            } for user in self.users]
        })
        serializer.is_valid()
        tournament = serializer.save()

        # Assert that the tournament is saved properly
        self.assertFalse(tournament._state.adding)
        self.assertEqual(tournament.name, name)
        self.assertEqual(tournament.participants.count(),
                         self.num_participants)

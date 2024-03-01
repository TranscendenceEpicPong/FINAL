import json
import random
from typing import List

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from core.models import EpicPongUser
from tournament_app.models import Tournament, RegistrationTournament
from tournament_app.serializers import TournamentSerializer, ParticipantSerializer


def create_tournament(number_participants: int, tournament_name: str = "Tournament"):
    tournament = Tournament.objects.create(name=tournament_name)

    try:
        new_id = RegistrationTournament.objects.latest('id').id + 1
    except RegistrationTournament.DoesNotExist:
        new_id = 1
    for i in range(new_id, new_id + number_participants):
        tournament.participants.create(
            user=get_user_model().objects.create_user(
                username=f'user{i}'
            )
        )

    return tournament


class TournamentsBaseTest(TestCase):
    def setUp(self):
        self.tournament = create_tournament(8)
        self.tournament_path = f"/tournaments/{self.tournament.id}/"

        creds = {
            "username": "john",
            "password": "johnpassword"
        }
        get_user_model().objects.create_user(**creds)

        # This doesn't work because we don't have a real authentication backend
        # self.client.login(**creds)

        self.client.post('/authentication/login', json.dumps(creds), content_type='application/json')


# Create your tests here.
class TournamentsTestCase(TournamentsBaseTest):
    def test_get_tournament_while_not_registered(self):
        response = self.client.get(self.tournament_path)
        self.assertEqual(response.status_code, 403)


class TournamentApiTestCase(APITestCase, TournamentsBaseTest):
    base_path = "/tournaments"

    def setUp(self):
        self.tournament = create_tournament(8)
        self.detail_path = f"{self.base_path}/{self.tournament.id}"
        self.tournament_path = f"{self.detail_path}/"

        creds = {
            "username": "john",
            "password": "johnpassword"
        }

        self.user = get_user_model().objects.create_user(**creds)

        # This doesn't work because we don't have a real authentication backend
        # self.client.force_authenticate(user=self.user)

        response = self.client.get("/server_info/")
        csrf_token = response.cookies.get('csrftoken')
        response = self.client.post('/authentication/login', creds, headers={
            "X-CSRFToken": csrf_token.value
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_tournament_while_not_registered(self):
        response = self.client.get(self.tournament_path)
        self.assertEqual(response.status_code, 403)

    def test_get_tournament_while_registered(self):
        self.tournament.participants.create(user=self.user)
        response = self.client.get(self.tournament_path)
        self.assertEqual(response.status_code, 200)

    def test_list_tournaments(self):
        response = self.client.get(f"{self.base_path}/")
        self.assertEqual(len(response.data), 0)
        my_tournament = create_tournament(8, "Test Tournament")
        my_tournament.participants.create(user=self.user)
        response = self.client.get(f"{self.base_path}/")
        self.assertEqual(len(response.data), 1)

    def test_create_tournament_without_current_user(self):
        response = self.client.post(self.tournament_path, {
            "name": "Test tournament",
            "participants": [
                {
                    "username": f"user{i}"
                } for i in range(8)
            ]
        })
        self.assertEqual(response.status_code, 403)

    def test_create_tournament_with_current_user(self):
        response = self.client.post(self.tournament_path, {
            "name": "Test tournament",
            "participants": [*[
                {
                    "username": f"user{i}"
                } for i in range(8)
            ], {
                "username": self.user.usermame
            }]
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["creator"], self.user.username)
        for participant in response.data["participants"]:
            self.assertFalse(participant["is_active"])

    def test_register_tournament(self):
        participant = self.tournament.participants.create(user=self.user)
        alias = "toto"
        response = self.client.post(f"{self.detail_path}/register/", {
            "alias": alias
        }, format='json')
        self.assertEqual(response.status_code, 202)

        participant.refresh_from_db()
        self.assertEqual(participant.alias, alias)
        self.assertTrue(participant.is_active)

    def test_launch_tournament(self):
        pass


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

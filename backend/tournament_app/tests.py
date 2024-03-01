import json
import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase
from tournament_app.models import Tournament, RegistrationTournament


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


class TournamentApiTestCase(APITestCase):
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
        self.assertEqual(response.status_code, 404)

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
        response = self.client.post(f"{self.base_path}/", {
            "name": "Test tournament",
            "participants": [
                {
                    "user": f"user{i}"
                } for i in range(1, 8)
            ]
        }, format="json")
        self.assertContains(response,
                            "The creator must be in the participants",
                            status_code=400)

    def test_create_tournament_with_current_user(self):
        response = self.client.post(f"{self.base_path}/", {
            "name": "Test tournament",
            "participants": [*[
                {
                    "user": f"user{i}"
                } for i in range(1, 8)
            ], {
                                 "user": self.user.username
                             }]
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["creator"]['user_name'], self.user.username)
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
        self.tournament.participants.create(user=self.user, is_creator=True)
        self.tournament.participants.update(is_active=True)
        response = self.client.post(f"{self.detail_path}/launch/")
        self.assertEqual(response.status_code, 201)


class PhasesTestCase(TestCase):
    def start_next_phase(self, tournament: Tournament):
        tournament.update_tournament_results()
        tournament.start_next_phase()

    def assertNextPhase(self, tournament, expected: Tournament.Phases):
        self.start_next_phase(tournament)
        self.assertEqual(tournament.phase, expected)

    def test_tournament_not_started(self):
        tournament = create_tournament(3)
        tournament.participants.update(is_active=True)
        self.assertEqual(tournament.phase, Tournament.Phases.NOT_STARTED)
        self.assertNextPhase(tournament, Tournament.Phases.POOL_PHASE)

    def test_three_participants(self):
        tournament = create_tournament(3)
        tournament.participants.update(is_active=True)
        self.start_next_phase(tournament)
        self.assertNextPhase(tournament, Tournament.Phases.FINAL_PHASE)

    def test_four_participants(self):
        for i in range(4, 8):
            # print(f"Test with {i} participants")
            tournament = create_tournament(i)
            tournament.participants.update(is_active=True)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.SEMI_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.FINAL_PHASE)

    def test_eight_participants(self):
        for i in range(8, 16):
            tournament = create_tournament(i)
            tournament.participants.update(is_active=True)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.QUARTER_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.SEMI_PHASE)

    def test_sixteen_participants(self):
        for i in range(16, 21):
            # print(f"\nTest with {i} participants")
            tournament = create_tournament(i)
            tournament.participants.update(is_active=True)
            self.start_next_phase(tournament)
            self.assertNextPhase(tournament, Tournament.Phases.EIGHT_PHASE)
            self.assertNextPhase(tournament, Tournament.Phases.QUARTER_PHASE)


class ScoreTest(TestCase):
    def setUp(self):
        self.tournament = create_tournament(8)
        self.tournament.participants.update(is_active=True)
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

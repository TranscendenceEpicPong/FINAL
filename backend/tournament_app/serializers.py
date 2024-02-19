from .models import *
from rest_framework import serializers
from django.urls import reverse
from core.models import EpicPongUser


class TournamentSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    number_of_participants = serializers.SerializerMethodField(read_only=True)
    ranking = serializers.SerializerMethodField(read_only=True)
    is_open = serializers.BooleanField()
    matches = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'creator', 'participants',
            'number_of_participants', 'ranking',
            'is_open', 'matches', 'phase'
        ]

    def get_creator(self, tournament):
        creator: RegistrationTournament = tournament.creator
        creator_info = {
            'user_id': creator.user.id,
            'user_name': creator.user.username,
            'alias': creator.alias
        }
        return creator_info

    def get_participants(self, tournament):
        participants_info = []
        for registration in tournament.participants.all():
            participant_info = {
                'id': registration.user.id,
                'username': registration.user.username,
                'alias': registration.alias,
            }
            participants_info.append(participant_info)
        return participants_info

    def get_ranking(self, tournament):
        ranking = tournament.get_ranking_dict()
        ranking_info = []
        for rank, user in enumerate(ranking, start=1):
            ranking_info.append({
                "rank": rank,
                "username": user["user"].username,
                "alias": user["alias"],
                "points": user["points"],
                "goal_average": user["goal_average"],
                "goal_conceded": user["goal_conceded"]
            })
        return ranking_info

    def get_matches(self, tournament):
        matches_info = []
        for match in tournament.matches.all():
            match_info = {
                'player1': {
                    'id': match.player1.id,
                    'username': match.player1.username,
                    'alias': match.player1.registrationtournament_set.get(
                        tournament=tournament
                    ).alias,
                },
                'player2': {
                    'id': match.player2.id,
                    'username': match.player2.username,
                    'alias': match.player2.registrationtournament_set.get(
                        tournament=tournament
                    ).alias,
                },
                'phase': match.phase,
                'score_player1': match.score_player1,
                'score_player2': match.score_player2,
            }
            matches_info.append(match_info)
        return matches_info

    def get_number_of_participants(self, tournament):
        return tournament.participants.count()


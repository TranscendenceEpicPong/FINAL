from .models import *
from rest_framework import serializers
from django.urls import reverse
from core.models import EpicPongUser


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = RegistrationTournament
        fields = ["user", "alias"]
        read_only_fields = ["is_active"]


class TournamentSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    participants = ParticipantSerializer(many=True)
    number_of_participants = serializers.SerializerMethodField(read_only=True)
    is_open = serializers.BooleanField()
    matches = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'creator', 'participants',
            'number_of_participants', 'is_open',
            'matches', 'phase'
        ]

    def get_creator(self, tournament):
        creator: RegistrationTournament = tournament.creator
        creator_info = {
            'user_id': creator.user.id,
            'user_name': creator.user.username,
            'alias': creator.alias
        }
        return creator_info

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

from django.db import transaction

from .models import *
from rest_framework import serializers


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=get_user_model().objects.all())
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = RegistrationTournament
        fields = ["user", "alias", "is_creator", "is_active"]

    def validate(self, data):
        if data.get('alias', None) and len(data['alias']):
            data['is_active'] = True
        return data


class TournamentSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    participants = ParticipantSerializer(many=True)
    number_of_participants = serializers.SerializerMethodField(read_only=True)
    matches = serializers.SerializerMethodField(read_only=True)
    phase = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    @property
    def current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user

    class Meta:
        model = Tournament
        fields = [
            'name', 'creator', 'participants',
            'number_of_participants', 'matches',
            'id', 'phase'
        ]

    def validate_participants(self, participants: list):
        """
        Validate participants
            - Number of participants
            - There is one creator
            - The creator is the current user

        @param participants:
        @return:
        """
        if len(participants) < MIN_PARTICIPANTS:
            raise serializers.ValidationError("Not enough participants")

        if len(participants) > MAX_PARTICIPANTS:
            raise serializers.ValidationError("Too many participants")

        creators = [p['is_creator'] for p in participants
                    if p.get('is_creator', False)]

        if len(creators) > 1:
            raise serializers.ValidationError("There must be exactly one creator")
        elif len(creators) == 1:
            creator = creators[0]
            if creator['user'] != self.current_user:
                raise serializers.ValidationError("The creator must be the current user")
            return participants
        else:
            has_creator = False

            def set_current_user_as_creator(participant):
                nonlocal has_creator
                if participant['user'] == self.current_user:
                    participant['is_creator'] = True
                    has_creator = True
                return participant

            participants = list(map(
                set_current_user_as_creator,
                participants
            ))

            if not has_creator:
                raise serializers.ValidationError("The creator must be in the participants")

        return participants

    @transaction.atomic
    def create(self, validated_data):
        participants = validated_data.pop('participants')
        tournament = Tournament(**validated_data)
        tournament.save()
        for participant in participants:
            tournament.participants.create(**participant)
        return tournament

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
                'winner': getattr(match.get_winner(), 'username', None),
                'phase': match.phase,
                'state': match.state,
                'score_player1': match.score_player1,
                'score_player2': match.score_player2,
            }
            matches_info.append(match_info)
        return matches_info

    def get_number_of_participants(self, tournament):
        return tournament.participants.count()

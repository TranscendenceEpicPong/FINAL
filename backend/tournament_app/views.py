from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import EpicPongUser
from .permissions import IsParticipant, IsCreator, NotStarted
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet
import json


# class TournamentViewSet(mixins.CreateModelMixin,
#                         mixins.RetrieveModelMixin,
#                         mixins.ListModelMixin,
#                         viewsets.GenericViewSet):
class TournamentViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        qs: 'QuerySet[Tournament]' = Tournament.objects.all()
        user = self.request.user
        qs = qs.filter(participants__user=user).distinct()
        return qs

    @action(detail=True,
            methods=['post'],
            permission_classes=[*permission_classes,
                                IsCreator,
                                NotStarted])
    def launch(self, request, pk=None):
        tournament = self.get_object()

        if tournament.active_count < MIN_PARTICIPANTS:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': "'You need at least 3 registered participants!"})

        tournament.start_next_phase()
        return Response(status=status.HTTP_201_CREATED,
                        data={
                            'status': 'Tournament started!',
                            'tournament': self.get_serializer(tournament).data
                        })

    @action(detail=True,
            methods=['post'],
            permission_classes=[*permission_classes,
                                NotStarted])
    def register(self, request, pk=None):
        user: EpicPongUser = request.user
        data = request.data
        if 'alias' not in data or not data['alias']:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': 'You must provide an alias!'})
        data['user'] = user.username

        tournament: Tournament = self.get_object()

        try:
            participant = tournament.participants.get(user=user)
        # except RegistrationTournament.DoesNotExist:
        # It is already handled in IsParticipant permission
        except RegistrationTournament.MultipleObjectsReturned:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': "You can't register more than once!"})

        serializer = ParticipantSerializer(data=data,
                                           instance=participant)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_202_ACCEPTED)

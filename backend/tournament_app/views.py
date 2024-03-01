from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsParticipant, IsCreator, NotStarted
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet
import json


class TournamentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated, IsParticipant]

    def get_queryset(self):
        qs: 'QuerySet[Tournament]' = Tournament.objects.all()
        user = self.request.user
        qs.filter(participants__user=user).distinct()
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsCreator, NotStarted])
    def launch(self):
        tournament = self.get_object()

        serializer = self.get_serializer(tournament)
        serializer.is_valid(raise_exception=True)

        tournament.start_next_phase()
        return Response(status=status.HTTP_201_CREATED,
                        data={
                            'status': 'Tournament started!',
                            'tournament': serializer.data
                        })

    @action(detail=True, methods=['post'], permission_classes=[NotStarted])
    def register(self, request, pk):
        user: EpicPongUser = request.user
        data = json.loads(request.body)
        if 'alias' not in data or not data['alias']:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': 'You must provide an alias!'})
        data['user'] = user.username

        tournament: Tournament = self.get_object()
        participant = tournament.participants.get(user=user)
        participant.is_active = True
        serializer = ParticipantSerializer(data=data,
                                           instance=participant)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_202_ACCEPTED)

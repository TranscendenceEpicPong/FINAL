from rest_framework import viewsets, mixins
from .serializers import *
from .models import *
from django.views.decorators.http import require_POST, require_GET
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet
from django.http import JsonResponse
import json
from .status import *


class TournamentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs: 'QuerySet[Tournament]' = Tournament.objects.all()
        user = self.request.user
        qs.filter(participants__user=user).distinct()
        return qs


@require_POST
def start(request, tournament_id):
    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist:
        return JsonResponse(StatusJoin.NOT_FOUND.value)

    if tournament.phase != 'no':
        return JsonResponse(StatusStart.ALREADY_STARTED.value)

    if tournament.participants.count() < MIN_PARTICIPANTS:
        return JsonResponse(StatusStart.NOT_ENOUGH_PARTICIPANTS.value)

    tournament.start_next_phase()

    return JsonResponse(StatusStart.SUCCESS.value)


# POST
# create a tournament
@require_POST
def create(request):
    user = request.user
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(Status.INVALID_SYNTAXE.value)

    alias = body.get('alias')
    if not alias or type(alias) != str:
        return JsonResponse(StatusCreating.BAD_FORMAT_ALIAS.value)
    if len(alias) == 0:
        return JsonResponse(StatusCreating.EMPTY_ALIAS.value)

    name = body.get('name')
    if not name or type(name) != str:
        return JsonResponse(StatusCreating.BAD_FORMAT_NAME.value)
    if not name or len(name) == 0:
        return JsonResponse(StatusCreating.EMPTY_NAME.value)

    max_participants = body.get('max_participants')
    if not max_participants or type(max_participants) != int:
        return JsonResponse(StatusCreating.INVALID_MAX_PARTICIPANTS.value)

    if max_participants < MIN_PARTICIPANTS or max_participants > MAX_PARTICIPANTS:
        return JsonResponse(StatusCreating.INVALID_MAX_PARTICIPANTS.value)

    try:
        Tournament.objects.get(name=name)
        return JsonResponse(StatusCreating.ALREADY_EXIST.value)
    except Tournament.DoesNotExist:
        pass

    tournament = Tournament.objects.create(name=name, max_participants=max_participants)
    RegistrationTournament.objects.create(user=user, tournament=tournament, alias=alias)

    return JsonResponse(StatusCreating.SUCCESS.value)


# join a tournament
@require_POST
def join(request):
    user = request.user
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(Status.INVALID_SYNTAXE.value)
    # service = TournamentService(body.get('name'))

    alias = body.get('alias')
    if not alias or len(alias) == 0:
        return JsonResponse(StatusJoin.EMPTY_ALIAS.value)

    tournament_name = body.get('name')
    if not tournament_name or len(tournament_name) == 0:
        return JsonResponse(StatusJoin.EMPTY_TOURNAMENT_NAME.value)

    try:
        tournament = Tournament.objects.get(name=tournament_name, is_open=True)
    except Tournament.DoesNotExist:
        return JsonResponse(StatusJoin.CLOSED.value)

    if RegistrationTournament.objects.filter(user=user, tournament=tournament).exists():
        return JsonResponse(StatusJoin.ALREADY_REGISTERED.value)

    if tournament.participants.count() >= tournament.max_participants:
        return JsonResponse(StatusJoin.FULL.value)

    registration, created = RegistrationTournament.objects.get_or_create(user=user, tournament=tournament,
                                                                         defaults={'alias': alias})

    if not created:
        registration.alias = alias
        registration.save()

    return JsonResponse(StatusJoin.SUCCESS.value)

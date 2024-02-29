from rest_framework import permissions

from tournament_app.models import Tournament


class IsCreator(permissions.BasePermission):
    message = 'You must be the creator of the tournament.'

    def has_object_permission(self, request, view, obj):
        if obj.creator == request.user:
            return True
        return False


class IsParticipant(permissions.BasePermission):
    message = 'You must be a participant of the tournament.'

    def has_object_permission(self, request, view, obj: Tournament):
        if obj.participants.filter(user=request.user).count():
            return True
        return False


class NotStarted(permissions.BasePermission):
    message = 'The tournament is already started.'

    def has_object_permission(self, request, view, obj: Tournament):
        if obj.phase == Tournament.Phases.NOT_STARTED:
            return True
        return False

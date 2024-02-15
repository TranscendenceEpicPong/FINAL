from django.shortcuts import render
from .models import Chats
from django.contrib.auth import get_user, get_user_model
from django.db.models import Q
from django.http import JsonResponse
from friends.models import Friends

# Create your views here.

def user(request, username):
    user = get_user(request)
    try:
        other = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        return JsonResponse({'message': 'Utilisateur introuvable'}, status=404)
    try:
        friend = Friends.objects.get(user=user.pk, friend=other.id)
    except Friends.DoesNotExist:
        return JsonResponse({'message': 'Vous n\'êtes pas amis'}, status=403)

    chats = Chats.objects.filter(Q(receiver=user.pk, sender=other.id) | Q(sender=user.pk, receiver=other.id))
    return JsonResponse({'chats': list(chats.values())})
from django.shortcuts import render
from .models import Chats
from django.contrib.auth import get_user, get_user_model
from django.db.models import Q
from django.http import JsonResponse
from friends.models import Friends
from core.helpers import get_response

# Create your views here.
def index(request):
    user = get_user(request)
    chats = Chats.objects.filter(Q(receiver=user.pk) | Q(sender=user.pk))
    messages = []
    for chat in chats:
        messages.append({
            "sender": chat.sender.username,
            "receiver": chat.receiver.username,
            "content": chat.content
        })

    return JsonResponse(messages, safe=False, status=200)

def user(request, username):
    user = get_user(request)
    other = get_user_model().objects.filter(username=username).first()
    if other == None:
        return get_response({'message': 'Utilisateur introuvable', "status": 404})

    if user.id == other.id:
        return get_response({'message': 'Vous ne pouvez pas vous envoyer de message à vous même', "status": 403})

    friend = Friends.objects.filter(user=user.pk, friend=other.id).first()
    if friend == None:
        return get_response({'message': 'Vous n\'êtes pas amis', "status": 403})

    chats = Chats.objects.filter(Q(receiver=user.pk, sender=other.id) | Q(sender=user.pk, receiver=other.id))
    messages = []
    for chat in chats:
        messages.append({
            "sender": chat.sender.username,
            "receiver": chat.receiver.username,
            "content": chat.content
        })

    return JsonResponse(messages, safe=False, status=200)
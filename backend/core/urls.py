"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

import core.views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'tournaments', views.TournamentViewSet)
# router.register(r'tournaments/(?P<tournament_id>\d+)/ranking', views.TournamentRankingViewSet, basename='tournament-ranking')
# router.register(r'tournaments/(?P<tournament_id>\d+)/matches', views.TournamentMatchViewSet, basename='tournament-match')
# router.register(r'tournaments/(?P<tournament_id>\d+)/participants', views.TournamentParticipantsViewSet, basename='tournament-participants')


# router.register(r'tournaments/create/', views.TournamentCreateViewSet, basename='tournament-create')
# router.register(r'tournaments/join/', views.JoinTournamentViewSet.as_view({'post', 'update'}), basename='tournament-join')
# router.register(r'tournaments/(?P<tournament_id>\d+)/start/', views.StartTournamentViewSet, basename='start-tournament')


urlpatterns = [
    path('', core.views.template, name='template'),
    path('authentication/register', core.views.register, name='register'),
    path('friends', core.views.friends, name='friends'),
]

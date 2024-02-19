from collections.abc import Iterable

from django.contrib.auth import get_user_model
from django.db import models
import random
from itertools import zip_longest
import logging  # error

from django.db.models import QuerySet

MIN_PARTICIPANTS = 3
MAX_PARTICIPANTS = 20

PHASE_LIMITS = [
    ('no', MAX_PARTICIPANTS),
    ('pool', MAX_PARTICIPANTS),
    ('eighth', 16),
    ('quarter', 8),
    ('semi', 4),
    ('final', 2),
]


class Tournament(models.Model):
    class Phases(models.TextChoices):
        NOT_STARTED = 'no'
        POOL_PHASE = 'pool'
        EIGHT_PHASE = 'eight'
        QUARTER_PHASE = 'quarter'
        SEMI_PHASE = 'semi'
        FINAL_PHASE = 'final'

    name = models.CharField(max_length=50)
    is_open = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(default=20)
    phase = models.CharField(choices=Phases,
                             default=Phases.NOT_STARTED)

    def __str__(self):
        return f"{self.name} (Creator: {self.creator.alias})"

    @property
    def creator(self):
        return self.participants.filter(is_creator=True).first() \
            or self.participants.first()

    @property
    def is_full(self):
        return self.participants.count() >= self.max_participants

    @property
    def ranking(self) -> 'QuerySet[RegistrationTournament]':
        return self.participants.filter(is_active=True).order_by(
            '-points',
            '-goal_average',
            'goal_conceded',
        )

    @property
    def phase_index(self):
        phases_list = [
            phase[0] for phase in self.Phases.choices
        ]
        return phases_list.index(self.phase)

    @property
    def active_participants(self):
        return self.participants.filter(is_active=True)

    @property
    def active_count(self):
        return self.active_participants.count()

    @property
    def current_matches(self):
        return self.matches.filter(phase=self.phase)

    def get_next_phase(self):
        # print("Get next phase")

        if self.phase == self.Phases.NOT_STARTED:
            return self.Phases.POOL_PHASE

        if self.phase == self.Phases.FINAL_PHASE:
            return None

        if self.phase == self.Phases.POOL_PHASE and self.active_count < MAX_PARTICIPANTS:
            phase_index = self.phase_index
            while self.active_count < PHASE_LIMITS[phase_index][1]:
                phase_index += 1
        else:
            phase_index = self.phase_index + 1

        value = self.Phases.choices[phase_index][0]
        return self.Phases(value)

    def start_next_phase(self):
        # Check amount of participants
        if MIN_PARTICIPANTS > self.participants.count() > MAX_PARTICIPANTS:
            logging.error(f'Tournament "{self.name}" invalid number of participants.')
            raise Exception("Number of participants out of range")

        next_phase = self.get_next_phase()
        if next_phase is None:
            raise Exception("No more phases")

        # print(f"Next phase: {next_phase}")

        self.phase = next_phase
        self.save()

        if self.phase not in [self.Phases.NOT_STARTED, self.Phases.POOL_PHASE]:
            self.eliminate_participants()

        if self.phase != self.Phases.NOT_STARTED:
            self.organize_next_matches()

    def get_ranking_dict(self):
        return [{
            'user': participant.user,
            'alias': participant.alias,
            'points': participant.points,
            'goal_average': participant.goal_average,
            'goal_conceded': participant.goal_conceded
        } for participant in self.ranking]

    def eliminate_participants(self):
        limit = PHASE_LIMITS[self.phase_index][1]
        ids_to_eliminate = self.ranking[limit:].values_list('id', flat=True)
        # print(f"Eliminating {ids_to_eliminate.count()} participants")
        self.ranking.filter(id__in=ids_to_eliminate).update(is_active=False)
        # print(f"Remaining {self.active_count} participants")

    def organize_next_matches(self):
        if self.phase == self.Phases.POOL_PHASE:
            return self.organize_pool_matches()

        participants = self.active_participants
        half = self.active_count / 2
        pairs = list(zip_longest(
            participants[:half], reversed(participants[half:])
        ))
        for i, pair in enumerate(pairs, start=1):
            match = Match.objects.create(
                tournament=self,
                player1=pair[0].user,
                player2=pair[1].user,
                phase=self.phase,
            )

    def organize_pool_matches(self):
        participants_list_2free = list(self.participants.all())
        random.shuffle(participants_list_2free)
        participants_list_1free = []
        i = 0
        while participants_list_2free or participants_list_1free:
            if participants_list_2free:
                player1 = random.choice(participants_list_2free)
                participants_list_2free.remove(player1)

                if participants_list_2free:
                    opponent1 = random.choice(participants_list_2free)
                    participants_list_2free.remove(opponent1)
                    participants_list_1free.append(opponent1)
                else:
                    opponent1 = random.choice(participants_list_1free)
                    participants_list_1free.remove(opponent1)

                if participants_list_2free:
                    opponent2 = random.choice(participants_list_2free)
                    participants_list_2free.remove(opponent2)
                    participants_list_1free.append(opponent2)
                else:
                    opponent2 = random.choice(participants_list_1free)
                    participants_list_1free.remove(opponent2)

                match1 = Match.objects.create(
                    tournament=self,
                    player1=player1.user,
                    player2=opponent1.user,
                    phase=self.Phases.POOL_PHASE,
                )
                match2 = Match.objects.create(
                    tournament=self,
                    player1=player1.user,
                    player2=opponent2.user,
                    phase=self.Phases.POOL_PHASE,
                )
            else:
                player1 = random.choice(participants_list_1free)
                participants_list_1free.remove(player1)

                opponent1 = random.choice(participants_list_1free)
                participants_list_1free.remove(opponent1)

                match = Match.objects.create(
                    tournament=self,
                    player1=player1.user,
                    player2=opponent1.user,
                    phase=self.Phases.POOL_PHASE,
                )

    def get_registered_player(self, user):
        return self.participants.get(user=user)

    def update_tournament_results(self):
        for match in self.current_matches:
            winner_user = match.get_winner()
            loser_user = match.get_loser()

            winner = self.participants.get(user=winner_user)
            winner.points += 3
            loser = self.participants.get(user=loser_user)

            #####################################################
            #                                                   #
            #  goal_average = goal scored - goal conceded       #
            #                                                   #
            #  e.g. :         player1 vs player2                #
            #                       3-2                         #
            #  player1 : goal_average = 1 ; goal_conceded = 2   #
            #  player2 : goal_average = -1 ; goal_conceded = 3  #
            #                                                   #
            #####################################################

            winner.goal_average += match.get_winner_score() - match.get_loser_score()
            winner.goal_conceded += match.get_loser_score()
            loser.goal_average += match.get_loser_score() - match.get_winner_score()
            loser.goal_conceded += match.get_winner_score()

            winner.save()
            loser.save()


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    player1 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='player1_matches')
    player2 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='player2_matches')
    phase = models.CharField(choices=Tournament.Phases)
    score_player1 = models.PositiveIntegerField(default=0)
    score_player2 = models.PositiveIntegerField(default=0)

    MATCH_STATE_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ]

    state = models.CharField(max_length=20, choices=MATCH_STATE_CHOICES, default='not_started')
    ready_player1 = models.BooleanField(default=False)
    ready_player2 = models.BooleanField(default=False)

    def get_winner(self):
        return self.player1 \
            if self.score_player2 < self.score_player1 \
            else self.player2

    def get_winner_score(self):
        return max([self.score_player1, self.score_player2])

    def get_loser(self):
        return self.player1 \
            if self.score_player2 > self.score_player1 \
            else self.player2

    def get_loser_score(self):
        return min([self.score_player1, self.score_player2])


class RegistrationTournament(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament,
                                   on_delete=models.CASCADE,
                                   related_name='participants')
    alias = models.CharField(max_length=50)
    is_creator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    points = models.PositiveIntegerField(default=0)
    goal_average = models.IntegerField(default=0)
    goal_conceded = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('tournament', 'alias')

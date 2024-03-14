from django.contrib.auth import get_user_model
from django.db import models
import random
from itertools import zip_longest
import logging  # error
from channels.layers import get_channel_layer
from django.db.models import QuerySet
from asgiref.sync import sync_to_async, async_to_sync
from game.status import Status

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
    phase = models.CharField(choices=Phases,
                             default=Phases.NOT_STARTED)

    def __str__(self):
        return f"{self.name} (Creator: {self.creator.alias})"

    @property
    def creator(self):
        return self.participants.filter(is_creator=True).first() \
            or self.participants.first()

    @property
    def ranking(self) -> 'QuerySet[RegistrationTournament]':
        return self.active_participants.order_by(
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

        prev_phase = self.phase

        next_phase = self.get_next_phase()
        if next_phase is None:
            raise Exception("No more phases")

        # print(f"Next phase: {next_phase}")

        self.phase = next_phase
        self.save()

        if self.phase not in [self.Phases.NOT_STARTED, self.Phases.POOL_PHASE]:
            self.eliminate_participants(prev_phase)

        if self.phase == self.Phases.POOL_PHASE:
            self.participants.filter(is_active=False).delete()

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

    def eliminate_participants(self, prev_phase):
        if prev_phase == self.Phases.POOL_PHASE:
            limit = PHASE_LIMITS[self.phase_index][1]
            ids_to_eliminate = self.ranking[limit:].values_list('id', flat=True)
            # print(f"Eliminating {ids_to_eliminate.count()} participants")
            self.ranking.filter(id__in=ids_to_eliminate).update(is_active=False)
            # print(f"Remaining {self.active_count} participants")
        else:
            losers = [match.get_loser() for match in self.matches.filter(
                phase=prev_phase
            )]
            self.participants.filter(user__in=losers).update(is_active=False)

    def notify(self, match):
        async_to_sync(get_channel_layer().group_send)(
            f"core-{match.player1.id}",
            {
                'type': 'send_alert',
                'content': f"Tournois: {match.tournament.name}. Un nouveau match est disponible contre {match.player2.alias}",
            }
        )
        async_to_sync(get_channel_layer().group_send)(
            f"core-{match.player2.id}",
            {
                'type': 'send_alert',
                'content': f"Tournois: {match.tournament.name}. Un nouveau match est disponible contre {match.player1.alias}",
            }
        )

    def organize_next_matches(self):
        from game.models import Game as Match
        if self.phase == self.Phases.POOL_PHASE:
            return self.organize_pool_matches()

        participants = self.ranking
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
        from game.models import Game as Match
        participants_list_2free = list(self.participants.all())
        random.shuffle(participants_list_2free)
        participants_list_1free = []
        i = 0
        while len(participants_list_2free) > 0 or len(participants_list_1free) > 0:
            if len(participants_list_2free) > 0:
                player1 = random.choice(participants_list_2free)
                participants_list_2free.remove(player1)

                if len(participants_list_2free) > 0:
                    opponent1 = random.choice(participants_list_2free)
                    participants_list_2free.remove(opponent1)
                    participants_list_1free.append(opponent1)
                else:
                    opponent1 = random.choice(participants_list_1free)
                    participants_list_1free.remove(opponent1)

                if len(participants_list_2free) > 0:
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

            print(list(self.participants.all()))
            print("Winner:", winner_user)
            print("Loser:", loser_user)

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

    def check_next_phase(self):
        for match in self.current_matches:
            if match.status != Status.FINISHED.value:
                return False

        self.start_next_phase()


# class Match(models.Model):
#     tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
#     player1 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='player1_matches')
#     player2 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='player2_matches')
#     phase = models.CharField(choices=Tournament.Phases)
#     score_player1 = models.PositiveIntegerField(default=0)
#     score_player2 = models.PositiveIntegerField(default=0)

#     MATCH_STATE_CHOICES = [
#         ('not_started', 'Not Started'),
#         ('in_progress', 'In Progress'),
#         ('finished', 'Finished'),
#     ]

#     state = models.CharField(max_length=20, choices=MATCH_STATE_CHOICES, default='not_started')
#     ready_player1 = models.BooleanField(default=False)
#     ready_player2 = models.BooleanField(default=False)

    # def get_winner(self):
    #     if self.state != self.MATCH_STATE_CHOICES[-1][0]:
    #         return None
    #     return self.player1 \
    #         if self.score_player2 < self.score_player1 \
    #         else self.player2

    # def get_winner_score(self):
    #     return max([self.score_player1, self.score_player2])

    # def get_loser(self):
    #     if self.state != self.MATCH_STATE_CHOICES[-1][0]:
    #         return None
    #     return self.player1 \
    #         if self.score_player2 > self.score_player1 \
    #         else self.player2

    # def get_loser_score(self):
    #     return min([self.score_player1, self.score_player2])

    # def get_as_dict(self):
    #     return {
    #         'player1': {
    #             'id': self.player1.id,
    #             'username': self.player1.username,
    #             'alias': self.player1.registrationtournament_set.get(
    #                 tournament=self.tournament
    #             ).alias,
    #         },
    #         'player2': {
    #             'id': self.player2.id,
    #             'username': self.player2.username,
    #             'alias': self.player2.registrationtournament_set.get(
    #                 tournament=self.tournament
    #             ).alias,
    #         },
    #         'winner': getattr(self.get_winner(), 'username', None),
    #         'phase': self.phase,
    #         'state': self.state,
    #         'score_player1': self.score_player1,
    #         'score_player2': self.score_player2,
    #     }


class RegistrationTournament(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament,
                                   on_delete=models.CASCADE,
                                   related_name='participants')
    alias = models.CharField(max_length=50,
                             null=True,
                             blank=False)
    is_creator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    goal_average = models.IntegerField(default=0)
    goal_conceded = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('tournament', 'alias')

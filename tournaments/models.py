import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F
from shortuuid import ShortUUID

from playpro.abstract import TimestampAbstractModel
from users.models import School, User
from django.utils.translation import gettext_lazy as _


def tournament_upload_path():
    return f"tournaments/{uuid.uuid4()}"


def result_upload_path():
    return f"tournament_result/{uuid.uuid4()}"


class TournamentPlatform(TimestampAbstractModel, models.Model):

    name = models.CharField(max_length=255)


class Tournament(TimestampAbstractModel, models.Model):
    registration_open_date = models.DateTimeField()
    registration_close_date = models.DateTimeField()
    registration_check_in_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=tournament_upload_path())
    platforms = models.ManyToManyField(TournamentPlatform)
    team_size = models.PositiveIntegerField()
    playoff_array = ArrayField(
        ArrayField(models.IntegerField(), size=2), size=8, null=True
    )


class TournamentTeam(TimestampAbstractModel, models.Model):

    school = models.ForeignKey(School, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    captain = models.ForeignKey(User, on_delete=models.PROTECT)
    group_score = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    tournament_joined = models.BooleanField(default=False)

    class Meta:
        unique_together = ("captain", "tournament")

    def save(self, *args, **kwargs):
        should_create_captain = False
        if not self.pk:
            should_create_captain = True
        super().save(*args, **kwargs)
        if should_create_captain:
            TournamentTeamMember.objects.create(
                user=self.captain, invitation_accepted=True, team=self
            )

    @property
    def is_complete(self):
        return self.team_members.count() == self.tournament.team_size


class TournamentTeamMember(TimestampAbstractModel, models.Model):
    invitation_accepted = models.BooleanField(null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    team = models.ForeignKey(
        TournamentTeam, on_delete=models.CASCADE, related_name="team_members"
    )


class TournamentGroup(TimestampAbstractModel, models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.PROTECT, related_name="tournament_groups"
    )
    teams = models.ManyToManyField(TournamentTeam)


class TournamentMatch(TimestampAbstractModel, models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_winner = self.winner

    class StageChoices(models.TextChoices):
        PLAYOFF = "playoff", _("Playoff")
        GROUP = "group", _("Group")

    tournament = models.ForeignKey(
        Tournament, on_delete=models.PROTECT, related_name="tournament_matches"
    )
    stage = models.CharField(choices=StageChoices.choices, max_length=20)
    match_start = models.DateTimeField()
    winner = models.ForeignKey(
        TournamentTeam, on_delete=models.PROTECT, blank=True, null=True
    )
    is_contested = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    contest_screenshot = models.ImageField(
        upload_to=result_upload_path(), blank=True, null=True
    )
    contestants = models.ManyToManyField(TournamentTeam, related_name="matches")
    round_number = models.IntegerField(blank=True, null=True)
    chat_channel = models.CharField(
        default=ShortUUID(alphabet=settings.NOTIFICATION_CHARSET).random(length=15),
        max_length=15,
    )

    def _update_teams_score(self):
        self.winner.wins += 1
        self.winner.save()
        loser = [x for x in self.contestants.all() if x is not self.winner][0]
        loser.losses += 1
        loser.save()

    def save(self, *args, **kwargs):
        if self.winner != self.initial_winner and self.initial_winner:
            self.is_contested = True
        elif self.winner == self.initial_winner and self.initial_winner and not self.is_final:
            self.is_final = True
            self._update_teams_score()

        super().save(*args, **kwargs)

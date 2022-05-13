import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from shortuuid import ShortUUID

from playpro.abstract import TimestampAbstractModel
from tournaments.validators import ImageSizeValidator
from users.models import School, User
from django.utils.translation import gettext_lazy as _


def tournament_upload_path():
    return f"tournaments/{uuid.uuid4()}"


def result_upload_path(tournament_match, filename):
    return f"tournament_result/{tournament_match.tournament.name}/{','.join(tournament_match.contestants.values_list('name', flat=True))}{uuid.uuid4()}"


def create_match_chat():
    return ShortUUID(alphabet=settings.NOTIFICATION_CHARSET).random(length=15)


class TournamentPlatform(TimestampAbstractModel, models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TournamentGame(TimestampAbstractModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class GamerTagChoice(TimestampAbstractModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TournamentGamePlatformMap(TimestampAbstractModel, models.Model):

    platform = models.ForeignKey(TournamentPlatform, on_delete=models.PROTECT)
    game = models.ForeignKey(TournamentGame, on_delete=models.PROTECT)
    gamer_tag_types = models.ManyToManyField(GamerTagChoice)

    def __str__(self):
        return f"{self.platform.name} - {self.game.name}"


class Tournament(TimestampAbstractModel, models.Model):
    registration_open_date = models.DateTimeField()
    registration_close_date = models.DateTimeField()
    registration_check_in_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    logo = models.FileField(upload_to=tournament_upload_path())
    tournament_img = models.ImageField(
        upload_to=tournament_upload_path(), null=True, blank=True
    )
    platforms = models.ManyToManyField(TournamentPlatform)
    team_size = models.PositiveIntegerField()
    game = models.ForeignKey(TournamentGame, null=True, on_delete=models.PROTECT)
    playoff_array = ArrayField(
        ArrayField(models.IntegerField(), size=2), size=8, null=True, blank=True
    )
    match_logo = models.FileField(blank=True, null=True)

    def __str__(self):
        return f"{self.game} | {self.name} | {' '.join([str(x) for x in self.platforms.all()])}"


class TournamentTeam(TimestampAbstractModel, models.Model):

    school = models.ForeignKey(School, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT, related_name="tournament_teams")
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

    def __str__(self):
        return self.name


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
        self.initial_is_final = self.is_final

    class StageChoices(models.TextChoices):
        PLAYOFF = "playoff", _("Playoff")
        GROUP = "group", _("Group")

    tournament = models.ForeignKey(
        Tournament, on_delete=models.PROTECT, related_name="tournament_matches"
    )
    stage = models.CharField(choices=StageChoices.choices, max_length=20)
    match_start = models.DateTimeField(blank=True, null=True)
    winner = models.ForeignKey(
        TournamentTeam, on_delete=models.PROTECT, blank=True, null=True
    )
    is_contested = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    contest_screenshot = models.ImageField(
        upload_to=result_upload_path,
        blank=True,
        null=True,
        validators=[ImageSizeValidator(3)],
    )
    contestants = models.ManyToManyField(TournamentTeam, related_name="matches")
    round_number = models.IntegerField(blank=True, null=True)
    chat_channel = models.CharField(
        default=create_match_chat,
        max_length=15,
    )
    place_finished = models.IntegerField(blank=True, null=True)
    result_submitted = ArrayField(
        models.IntegerField(), size=2, blank=True, default=list
    )

    # def __str__(self):
    #     return f'{self.tournament} | {" - ".join(self.contestants.values_list("name", flat=True))}'

    def _update_teams_score(self):
        self.winner.wins += 1
        self.winner.save()
        loser = [x for x in self.contestants.all() if x is not self.winner][0]
        loser.losses += 1
        loser.save()

    def save(self, *args, **kwargs):
        if self.place_finished:
            super().save(*args, **kwargs)
        else:
            if self.winner != self.initial_winner and self.initial_winner:
                self.is_contested = True
            elif self.winner == self.initial_winner and self.initial_winner and not self.is_contested:
                self.is_final = True
            if not self.initial_is_final and self.is_final:
                self._update_teams_score()
            super().save(*args, **kwargs)

    def has_submitted_result(self, user):
        user_team = self.contestants.filter(team_members__user=user).first()
        return getattr(user_team, "pk", None) in self.result_submitted

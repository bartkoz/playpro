from django.db import models

from users.models import School, User
from django.utils.translation import gettext_lazy as _


class TournamentPlatform(models.Model):

    name = models.CharField(max_length=255)


class Tournament(models.Model):
    registration_open_date = models.DateTimeField()
    registration_close_date = models.DateTimeField()
    registration_check_in_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    logo = models.ImageField()
    platforms = models.ManyToManyField(TournamentPlatform)
    team_size = models.PositiveIntegerField()


class TournamentTeam(models.Model):

    school = models.ForeignKey(School, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    captain = models.ForeignKey(User, on_delete=models.PROTECT)
    group_score = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    # class Meta:
    #     unique_together = ('captain', 'tournament')

    def save(self, *args, **kwargs):
        should_create_captain = False
        if not self.pk:
            should_create_captain = True
        super().save(*args, **kwargs)
        if should_create_captain:
            TournamentTeamMember.objects.create(
                user=self.captain, invitation_accepted=True, team=self
            )


class TournamentTeamMember(models.Model):
    invitation_accepted = models.BooleanField(null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    team = models.ForeignKey(
        TournamentTeam, on_delete=models.CASCADE, related_name="team_members"
    )


class TournamentGroup(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    teams = models.ManyToManyField(TournamentTeam)


class TournamentMatch(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_winner = self.winner

    class StageChoices(models.TextChoices):
        PLAYOFF = "playoff", _("Playoff")
        GROUP = "group", _("Group")

    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    stage = models.CharField(choices=StageChoices.choices, max_length=20)
    match_start = models.DateTimeField()
    winner = models.ForeignKey(
        TournamentTeam, on_delete=models.PROTECT, blank=True, null=True
    )
    is_contested = models.BooleanField(blank=True, null=True)
    contest_screenshot = models.ImageField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.winner != self.initial_winner and self.initial_winner:
            self.is_contested = True
        super().save(*args, **kwargs)

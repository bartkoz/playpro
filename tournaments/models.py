from django.db import models

from users.models import School, User


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
    members = models.ManyToManyField(User, related_name="team_members")
    captain = models.ForeignKey(User, on_delete=models.PROTECT)

    # class Meta:
    #     unique_together = ('captain', 'tournament')

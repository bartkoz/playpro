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
    captain = models.ForeignKey(User, on_delete=models.PROTECT)

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

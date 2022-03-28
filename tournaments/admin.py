from django.contrib import admin

from tournaments.models import (
    TournamentPlatform,
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
    TournamentMatch,
)

admin.site.register(TournamentPlatform)
admin.site.register(Tournament)
admin.site.register(TournamentTeam)
admin.site.register(TournamentTeamMember)
admin.site.register(TournamentGroup)
admin.site.register(TournamentMatch)
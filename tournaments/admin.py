from django.contrib import admin

from tournaments.models import (
    TournamentPlatform,
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
    TournamentMatch,
    TournamentGame,
    GamerTagChoice,
    TournamentGamePlatformMap,
)

admin.site.register(TournamentPlatform)
admin.site.register(Tournament)
admin.site.register(TournamentTeam)
admin.site.register(TournamentTeamMember)
admin.site.register(TournamentGroup)
admin.site.register(TournamentMatch)
admin.site.register(TournamentGame)
admin.site.register(GamerTagChoice)
admin.site.register(TournamentGamePlatformMap)

from django.contrib import admin

from tournaments.models import TournamentPlatform, Tournament, TournamentTeam

admin.site.register(TournamentPlatform)
admin.site.register(Tournament)
admin.site.register(TournamentTeam)

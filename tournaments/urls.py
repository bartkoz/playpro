from django.urls import path, include
from rest_framework import routers

from tournaments.views import TournamentBaseViewSet, TeamViewSet

team_viewset = routers.SimpleRouter()
team_viewset.register(r"team", TeamViewSet, basename="tournament_teams")

tournament_base_router = routers.SimpleRouter()
tournament_base_router.register(r"", TournamentBaseViewSet)


urlpatterns = [
    path("", include(team_viewset.urls + tournament_base_router.urls)),
]

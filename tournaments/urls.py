from django.urls import path, include
from rest_framework import routers


app_name = "tournaments"

from tournaments.views import (
    TournamentBaseViewSet,
    TeamViewSet,
    RankingAPIView,
    InvitationViewSet,
    TournamentMatchViewSet,
)

team_viewset = routers.SimpleRouter()
team_viewset.register(r"team", TeamViewSet, basename="tournament_teams")

tournament_base_router = routers.SimpleRouter()
tournament_base_router.register(r"", TournamentBaseViewSet)

invitation_viewset = routers.SimpleRouter()
invitation_viewset.register(
    r"invitations", InvitationViewSet, basename="tournament_invitations"
)

tournament_viewset = routers.SimpleRouter()
tournament_viewset.register(
    r"matches", TournamentMatchViewSet, basename="tournament_matches"
)


urlpatterns = [
    path("rankings/", RankingAPIView.as_view()),
    path(
        "",
        include(
            team_viewset.urls
            + invitation_viewset.urls
            + tournament_viewset.urls
            + tournament_base_router.urls
        ),
    ),
]

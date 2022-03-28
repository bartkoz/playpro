from django.urls import path, include
from rest_framework import routers

from tournaments.views import (
    TournamentBaseViewSet,
    TeamViewSet,
    RankingAPIView,
    InvitationViewSet,
)

team_viewset = routers.SimpleRouter()
team_viewset.register(r"team", TeamViewSet, basename="tournament_teams")

tournament_base_router = routers.SimpleRouter()
tournament_base_router.register(r"", TournamentBaseViewSet)

invitation_viewset = routers.SimpleRouter()
invitation_viewset.register(
    r"invitations", InvitationViewSet, basename="tournament_invitations"
)


urlpatterns = [
    path("rankings/", RankingAPIView.as_view()),
    path(
        "",
        include(
            team_viewset.urls + invitation_viewset.urls + tournament_base_router.urls
        ),
    ),
]

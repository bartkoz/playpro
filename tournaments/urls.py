from django.urls import path, include
from rest_framework import routers

from tournaments.views import (
    TournamentBaseViewSet,
    TeamViewSet,
    InvitationViewSet,
    TournamentMatchViewSet,
    TournamentRankingsViewSet,
    ScheduleAPIView,
    TournamentStageAPIView,
)

app_name = "tournaments"

team_viewset = routers.SimpleRouter()
team_viewset.register(r"team", TeamViewSet, basename="tournament_teams")

tournament_base_viewset = routers.SimpleRouter()
tournament_base_viewset.register(r"", TournamentBaseViewSet)

invitation_viewset = routers.SimpleRouter()
invitation_viewset.register(
    r"invitations", InvitationViewSet, basename="tournament_invitations"
)

tournament_viewset = routers.SimpleRouter()
tournament_viewset.register(
    r"matches", TournamentMatchViewSet, basename="tournament_matches"
)

tournament_rankings_viewset = routers.SimpleRouter()
tournament_rankings_viewset.register(
    r"rankings", TournamentRankingsViewSet, basename="tournament_rankings"
)


urlpatterns = [
    path("schedule/", ScheduleAPIView.as_view()),
    path(
        "",
        include(
            team_viewset.urls
            + invitation_viewset.urls
            + tournament_viewset.urls
            + tournament_rankings_viewset.urls
            + tournament_base_viewset.urls
        ),
    ),
    path("tournament_status/<int:pk>/", TournamentStageAPIView.as_view()),
]

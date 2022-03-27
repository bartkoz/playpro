from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from tournaments.models import Tournament, TournamentTeam, TournamentTeamMember
from tournaments.serializers import (
    TournamentListSerializer,
    TournamentDetailSerializer,
    TeamCreateSerializer,
    TeamUpdateSerializer,
    TeamSerializer,
)
from users.models import User
from users.serializers import UserTeammatesSrializer


class TournamentBaseViewSet(ReadOnlyModelViewSet):
    queryset = Tournament.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TournamentListSerializer
        return TournamentDetailSerializer


class TeamViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        elif self.request.method in ["POST", "DELETE"]:
            return TeamUpdateSerializer
        return TeamSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ["update", "partial_update"]:
            context["obj"] = self.get_object()
        return context

    def get_queryset(self):
        return TournamentTeam.objects.filter(captain=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tournament = get_object_or_404(
            Tournament, pk=serializer.validated_data["tournament"]
        )
        obj = TournamentTeam(
            name=serializer.validated_data["name"],
            school=request.user.school,
            tournament=tournament,
            captain=request.user,
        )
        return Response({"id": obj.pk}, status=status.HTTP_201_CREATED)

    def _check_if_captain(self, tournament, user):
        if tournament.captain != user:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(methods=("get",), detail=False)
    def teammates(self, request):
        return Response(
            {
                "users": UserTeammatesSrializer(
                    User.objects.filter(school_id=request.user.school_id).data,
                    many=True,
                )
            }
        )

    @action(methods=("post", "delete", "get"), detail=True)
    def manage_team(self, request, *args, **kwargs):
        tournament_team = get_object_or_404(TournamentTeam, pk=kwargs["pk"])
        serializer = self.get_serializer_class()
        if request.method == "POST":
            self._check_if_captain(tournament_team, request.user)
            serializer(data=request.data).is_valid(raise_exception=True)
            user_id = serializer.validated_data["user"]
            invitation, _ = TournamentTeamMember.objects.get_or_create(
                user_id=user_id, team=tournament_team
            )
        elif request.method == "DELETE":
            self._check_if_captain(tournament_team, request.user)
            serializer(data=request.data).is_valid(raise_exception=True)
            user_id = serializer.validated_data["user"]
            get_object_or_404(
                TournamentTeamMember, tournament_team=tournament_team, user_id=user_id
            ).delete()
        return Response(
            serializer(
                tournament_team.team_members.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )

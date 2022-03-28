from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
)
from tournaments.serializers import (
    TournamentListSerializer,
    TournamentDetailSerializer,
    TeamCreateSerializer,
    TeamUpdateSerializer,
    TeamMemberUpdateSerializer,
    TeamMemberSerializer,
    InvitationSerializer,
    TournamentGroupSerializer,
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
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TeamUpdateSerializer
        elif self.request.method == "POST":
            return TeamMemberUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action != "create":
            context["obj"] = self.get_object()
        context["action"] = self.action
        return context

    def get_queryset(self):
        return TournamentTeam.objects.filter(captain=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tournament = Tournament.objects.get(
                pk=serializer.validated_data["tournament"]
            )
        except Tournament.DoesNotExist:
            return Response(
                {"error": "Tournament does not exist."}, status.HTTP_400_BAD_REQUEST
            )
        obj = TournamentTeam.objects.create(
            name=serializer.validated_data["name"],
            school=request.user.school,
            tournament=tournament,
            captain=request.user,
        )
        return Response({"id": obj.pk}, status=status.HTTP_201_CREATED)

    @staticmethod
    def _check_if_captain(tournament, user):
        if tournament.captain != user:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(methods=("get",), detail=False)
    def available_teammates(self, request):
        return Response(
            {
                "users": UserTeammatesSrializer(
                    User.objects.filter(school_id=request.user.school_id),
                    many=True,
                ).data
            }
        )

    @action(methods=("post", "delete", "get"), detail=True)
    def manage_team(self, request, *args, **kwargs):
        tournament_team = get_object_or_404(TournamentTeam, pk=kwargs["pk"])
        if request.method == "POST":
            serializer_class = self.get_serializer_class()
            self._check_if_captain(tournament_team, request.user)
            serializer = serializer_class(
                data=request.data, context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            if serializer.validated_data["action"] == "add":
                invitation, _ = TournamentTeamMember.objects.get_or_create(
                    user=user, team=tournament_team
                )
            elif serializer.validated_data["action"] == "delete":
                get_object_or_404(
                    TournamentTeamMember, team=tournament_team, user=user
                ).delete()
        return Response(
            TeamMemberSerializer(
                tournament_team.team_members.all(),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )


class InvitationViewSet(
    GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
):

    serializer_class = InvitationSerializer

    def get_queryset(self):
        return TournamentTeamMember.objects.filter(user=self.request.user)


class RankingAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            TournamentGroupSerializer(
                TournamentGroup.objects.filter(teams__team_members__user=request.user),
                many=True,
            ).data
        )

from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet

from notifications.signals import invitation_revoked, invitation_created
from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
    TournamentMatch,
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
    TournamentMatchSerializer,
    TournamentMatchUpdateSerializer,
    TournamentMatchContestantsSerializer,
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
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TeamUpdateSerializer
        elif self.action == "retrieve":
            return TournamentMatchContestantsSerializer
        elif self.request.method == "POST":
            return TeamMemberUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action != "create":
            context["obj"] = self.get_object()
        context["action"] = self.action
        return context

    def get_queryset(self):
        if self.action == "retrieve":
            return TournamentTeam.objects.all()
        return TournamentTeam.objects.filter(team_members__user=self.request.user)

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
        if tournament.captain == user:
            return True
        return False

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

    @action(methods=("post", "get"), detail=True)
    def manage_team(self, request, *args, **kwargs):
        tournament_team = get_object_or_404(TournamentTeam, pk=kwargs["pk"])
        if request.method == "POST":
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(
                data=request.data, context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            if serializer.validated_data["action"] == "add":
                if not self._check_if_captain(tournament_team, request.user):
                    Response(status=status.HTTP_403_FORBIDDEN)
                invitation, _ = TournamentTeamMember.objects.get_or_create(
                    user=user, team=tournament_team
                )
                invitation_created.send(instance=invitation, sender=None)
            elif serializer.validated_data["action"] == "delete":
                if (
                    not self._check_if_captain(tournament_team, request.user)
                    and user != request.user
                ):
                    Response(status=status.HTTP_403_FORBIDDEN)
                obj = get_object_or_404(
                    TournamentTeamMember, team=tournament_team, user=user
                )
                if obj.user != request.user:
                    invitation_revoked.send(instance=obj, sender=None)
                obj.delete()
                if self._check_if_captain(tournament_team, request.user):
                    if tournament_team.team_members.count() == 0:
                        tournament_team.delete()
                    else:
                        tournament_team.captain = (
                            tournament_team.team_members.order_by("created_at")
                            .first()
                            .user
                        )
                    tournament_team.save()
                return Response(status=status.HTTP_200_OK, data={"status": "ok"})
        return Response(
            TeamMemberSerializer(
                tournament_team.team_members.order_by("created_at"),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )


class InvitationViewSet(
    GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
):

    serializer_class = InvitationSerializer

    def get_queryset(self):
        return TournamentTeamMember.objects.filter(
            user=self.request.user, invitation_accepted__isnull=True
        )


class RankingAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            TournamentGroupSerializer(
                TournamentGroup.objects.filter(teams__team_members__user=request.user),
                many=True,
            ).data
        )


class TournamentMatchViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return TournamentMatchUpdateSerializer
        return TournamentMatchSerializer

    def get_queryset(self):
        return TournamentMatch.objects.filter(
            contestants__team_members__user=self.request.user
        )

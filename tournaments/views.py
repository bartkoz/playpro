import string
from datetime import datetime

from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from notifications.receivers import notify_captain_invitation_denied
from notifications.signals import invitation_revoked, invitation_created
from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
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
    TournamentMatchListSerializer,
    TournamentMatchContestSerializer,
    MatchesPlayoffSerializer,
)
from users.models import User
from users.serializers import UserTeammatesSrializer


class CustomPaginator(PageNumberPagination):
    page_size = 10


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

    @action(methods=("get",), detail=True)
    def available_teammates(self, request, *args, **kwargs):
        try:
            tournament = TournamentTeam.objects.get(pk=kwargs.get("pk")).tournament
        except TournamentTeam.DoesNotExist:
            return Response(
                {"errpr": "Team with given id does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "users": UserTeammatesSrializer(
                    User.objects.annotate(
                        has_team=Exists(
                            TournamentTeamMember.objects.filter(
                                team__tournament=tournament, user=OuterRef("pk")
                            )
                        )
                    ).filter(has_team=False, school_id=request.user.school_id),
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
                        return Response(
                            status=status.HTTP_200_OK, data={"status": "ok"}
                        )
                    else:
                        tournament_team.captain = (
                            tournament_team.team_members.order_by("created_at")
                            .first()
                            .user
                        )
                    tournament_team.save()
        return Response(
            TeamMemberSerializer(
                tournament_team.team_members.order_by("created_at"),
                many=True,
                # context=self.get_serializer_context(),
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # can be moved to avoid pointless update
        if instance.invitation_accepted == False:
            notify_captain_invitation_denied(instance)
            instance.delete()
        return Response(status=status.HTTP_200_OK, data={"status": "ok"})


class TournamentMatchViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    def get_serializer_class(self):
        if self.action == "screenshot_contest":
            return TournamentMatchContestSerializer
        if self.action in ["update", "partial_update"]:
            return TournamentMatchUpdateSerializer
        return TournamentMatchSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "retrieve":
            ctx["match_obj"] = self.get_object()
            ctx["user_team"] = [
                x
                for x in self.get_object().contestants.all()
                if self.request.user.pk in x.team_members.values_list("user", flat=True)
            ][
                0
            ]  # todo
        return ctx

    def get_queryset(self):
        qs = TournamentMatch.objects.filter(
            contestants__team_members__user=self.request.user
        ).order_by("match_start")
        if self.action == "list":
            return qs[:4]
        return qs

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer_class()
        user_team = obj.contestants.filter(team_members__user=request.user).first()
        if user_team.pk not in obj.result_submitted:
            serializer_obj = serializer(data=request.data)
            serializer_obj.is_valid(raise_exception=True)
            if serializer_obj.validated_data.get("winner") == "win":
                obj.winner = user_team
            else:
                opposing_team = list(obj.contestants.all())
                opposing_team.remove(user_team)
                opposing_team = opposing_team[0]
                obj.winner = opposing_team
            obj.result_submitted.append(user_team.pk)
            obj.save()
        if obj.is_contested:
            match_status = "contested"
        elif obj.is_final:
            match_status = (
                "winner"
                if self.request.user in obj.winner.team_members.all()
                else "loser"
            )
        else:
            match_status = "pending"
        return Response({"status": match_status})

    @action(methods=("patch", "put"), detail=True)
    def screenshot_contest(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"contest_screenshot": self.get_object().contest_screenshot.url},
            status=status.HTTP_200_OK,
        )


class TournamentRankingsViewSet(GenericViewSet, mixins.ListModelMixin):

    queryset = (
        Tournament.objects.all()
        .prefetch_related(
            "tournament_groups", "tournament_groups__teams__team_members__user"
        )
        .order_by("pk")
    )
    serializer_class = TournamentListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        if self.action in ["groups", "playoff"]:
            ctx["groups_names"] = self._get_groups_names(
                count=self.get_object().tournament_groups.count()
            )
        return ctx

    def _get_groups_names(self, count):
        if count > 26:
            additional_count = count - 26
            return (
                list(string.ascii_uppercase)
                + [x * 2 for x in string.ascii_uppercase][:additional_count]
            )
        return list(string.ascii_uppercase)[:count]

    @action(methods=("get",), detail=True)
    def groups(self, request, *args, **kwargs):
        return Response(
            TournamentGroupSerializer(
                self.get_object().tournament_groups,
                many=True,
                context=self.get_serializer_context(),
            ).data
        )

    @action(methods=("get",), detail=True)
    def playoff(self, request, *args, **kwargs):
        return Response(
            MatchesPlayoffSerializer(
                self.get_object()
                .tournament_matches.filter(stage=TournamentMatch.StageChoices.PLAYOFF)
                .order_by("round_number", "pk"),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )


class ScheduleAPIView(ListAPIView):

    serializer_class = TournamentMatchListSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return (
            TournamentMatch.objects.filter(
                # contestants__team_members__user=self.request.user,  # todo
                match_start__gte=datetime.utcnow(),
            )
            .order_by("match_start")
            .distinct()
        )


class TournamentStageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        tournament = get_object_or_404(Tournament, pk=kwargs["pk"])
        if tournament.registration_close_date > timezone.now():
            tournament_status = "registration_open"
        elif (
            tournament.tournament_matches.filter(
                stage=TournamentMatch.StageChoices.PLAYOFF
            ).count()
            > 0
        ):
            tournament_status = "playoff"
        else:
            tournament_status = "groups"
        return Response({"status": tournament_status})

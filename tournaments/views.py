from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from tournaments.models import Tournament, TournamentTeam
from tournaments.serializers import (
    TournamentListSerializer,
    TournamentDetailSerializer,
    TeamCreateSerializer,
    TeamUpdateSerializer,
)
from users.models import User
from users.serializers import UserTeammateserializer


class TournamentBaseViewSet(ReadOnlyModelViewSet):
    queryset = Tournament.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TournamentListSerializer
        return TournamentDetailSerializer


class TeamViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):

    permission_classes = ()

    def get_serializer_class(self):
        if self.action == "create":
            return TeamCreateSerializer
        return TeamUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ["update", "partial_update"]:
            context["obj"] = self.get_object()
        return context

    def get_queryset(self):
        # return TournamentTeam.objects.filter(captain=self.request.user)
        return TournamentTeam.objects.filter(captain=User.objects.first())

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

    # @action(methods=('post',), detail=True)
    # def new(self, request, *args, **kwargs):
    #     tournament = get_object_or_404(Tournament, pk=kwargs.get('pk'))
    #     # TournamentTeam
    #     return Response()

    @action(methods=("get",), detail=False)
    def teammates(self, request):
        return Response(
            {
                "users": UserTeammateserializer(
                    User.objects.filter(school_id=request.user.school_id).data,
                    many=True,
                )
            }
        )

from django.db.models import Sum, F
from rest_framework import serializers

from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
    TournamentMatch,
)
from django.utils.translation import gettext_lazy as _


class TournamentListSerializer(serializers.ModelSerializer):

    platforms = serializers.SerializerMethodField()

    def get_platforms(self, obj):
        return obj.platforms.values_list("name", flat=True)

    class Meta:
        model = Tournament
        fields = ("name", "logo", "pk", "platforms", "team_size")


class TournamentDetailSerializer(serializers.ModelSerializer):

    platforms = serializers.SerializerMethodField()

    def get_platforms(self, obj):
        return obj.platforms.values_list("name", flat=True)

    class Meta:
        model = Tournament
        fields = (
            "registration_open_date",
            "registration_close_date",
            "registration_check_in_date",
            "name",
            "logo",
            "platforms",
            "team_size",
        )


class TeamCreateSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=255)
    tournament = serializers.IntegerField()

    def validate(self, attrs):
        if TournamentTeam.objects.filter(
            captain=self.context["request"].user, tournament_id=attrs["tournament"]
        ).exists():
            raise serializers.ValidationError(
                _(
                    "You may only create one team per tournament. "
                    "If you wish to create new team you have to leave your current one."
                )
            )
        return attrs


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentTeam
        fields = ("name",)


class TeamMemberUpdateSerializer(serializers.ModelSerializer):

    action = serializers.ChoiceField(choices=(("add", "add"), ("delete", "delete")))

    class Meta:

        model = TournamentTeamMember
        fields = ("user", "action")

    def validate_user(self, value):
        team_obj = self.context["obj"]
        # if team_obj.captain == value:
        #     raise serializers.ValidationError(
        #         _("You cannot remove captain from the team.")
        #     )
        if (
            self.initial_data.get("action") == "add"
            and team_obj.team_members.count() >= team_obj.tournament.team_size
        ):
            raise serializers.ValidationError(
                _(
                    f"Team can oan consist of maximum of {team_obj.tournament.team_size} teammates."
                )
            )
        if value.is_in_team(team_obj):
            raise serializers.ValidationError(
                _(f"{value.full_name} is already part of a team in this tournament.")
            )
        if value.school != self.context["request"].user.school:
            raise serializers.ValidationError(
                _("You may only invite people from your schoool.")
            )
        return value


class TeamMemberSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.school_email", read_only=True)
    is_captain = serializers.SerializerMethodField()
    avatar = serializers.URLField(source="user.avatar.image.url", read_only=True)
    invitation_accepted = serializers.SerializerMethodField()
    user_pk = serializers.IntegerField(source="user.pk", read_only=True)

    class Meta:
        model = TournamentTeamMember
        fields = (
            "user_pk",
            "full_name",
            "email",
            "is_captain",
            "avatar",
            "invitation_accepted",
        )

    def get_is_captain(self, obj):
        return obj.team.captain == obj.user

    def get_invitation_accepted(self, obj):
        mapping = {None: "pending", False: "rejected", True: "accepted"}
        return mapping[obj.invitation_accepted]


class InvitationSerializer(serializers.ModelSerializer):

    tournament = serializers.CharField(source="team.tournament.name", read_only=True)
    number_of_players = serializers.IntegerField(
        source="team.tournament.team_size", read_only=True
    )
    platforms = serializers.SerializerMethodField()

    class Meta:
        model = TournamentTeamMember
        fields = ("tournament", "number_of_players", "platforms", "invitation_accepted")

    def get_platforms(self, obj):
        return obj.team.tournament.platforms.values_list("name", flat=True)

    def validate_invitation_accepted(self, obj):
        if self.instance.invitation_accepted is not None:
            raise serializers.ValidationError(
                _("Invitation has already been addressed.")
            )
        return obj

    def validate(self, attrs):
        if self.instance.user.is_in_team(self.instance.team):
            raise serializers.ValidationError(
                _(
                    f"You need to leave your current team in tournament {self.instance.team.tournament.name} to accept this invitation"
                )
            )
        return attrs


class TournamentGroupTeamSerializer(serializers.ModelSerializer):

    school = serializers.CharField(source="school.name")

    class Meta:
        model = TournamentTeam
        fields = ("school", "name", "wins", "losses")


class TournamentGroupSerializer(serializers.ModelSerializer):

    teams = serializers.SerializerMethodField()

    class Meta:
        model = TournamentGroup
        fields = ("teams", "tournament")

    def get_teams(self, obj):
        return TournamentGroupTeamSerializer(
            obj.teams.annotate(result=Sum(F("wins") - F("losses"))).order_by("-result"),
            many=True,
        ).data


class TournamentMatchContestantsSerializer(serializers.ModelSerializer):

    team_members = TeamMemberSerializer(many=True)

    class Meta:
        model = TournamentTeam
        fields = ("name", "team_members")


class TournamentMatchSerializer(serializers.ModelSerializer):

    contestants = TournamentMatchContestantsSerializer(many=True)
    tournament = serializers.CharField(source="tournament.name")
    winner = serializers.SerializerMethodField()

    class Meta:
        model = TournamentMatch
        fields = "__all__"

    def get_winner(self, obj):
        if obj.is_contested:
            return "contested"
        elif obj.is_final:
            return (
                "winner"
                if self.context["request"].user
                in self.context["instance"].winner.team_members
                else "loser"
            )
        else:
            return "pending"


class TournamentMatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentMatch
        fields = ("winner",)

from django.db.models import Sum, F
from rest_framework import serializers

from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
)
from django.utils.translation import gettext_lazy as _


class TournamentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ("name", "logo", "pk")


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
        obj = self.context["obj"]
        if obj.captain == value:
            raise serializers.ValidationError(
                _("You cannot remove captain from the team.")
            )
        if (
            self.initial_data.get("action") == "add"
            and obj.team_members.count() >= obj.tournament.team_size
        ):
            raise serializers.ValidationError(
                _(
                    f"Team can oan consist of maximum of {obj.tournament.team_size} teammates."
                )
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

    class Meta:
        model = TournamentTeamMember
        fields = (
            "pk",
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

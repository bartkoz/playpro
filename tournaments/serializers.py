from rest_framework import serializers

from tournaments.models import Tournament, TournamentTeam, TournamentTeamMember
from django.utils.translation import gettext_lazy as _


class TournamentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ("name", "logo")


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

    def validate_members(self, value):
        obj = self.context["obj"]
        value.remove(obj.captain)
        # TODO max team size
        # if obj.tournament.team_size < len(obj.tournament.members.count() + 1):
        #     raise serializers.ValidationError(
        #         _(
        #             f"Team can oan consist of maximum of {obj.tournament.team_size} teammates."
        #         )
        #     )
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

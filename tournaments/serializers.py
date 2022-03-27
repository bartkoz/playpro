from rest_framework import serializers

from tournaments.models import Tournament, TournamentTeam, TournamentTeamMember
from django.utils.translation import gettext_lazy as _

from users.models import User


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

        model = TournamentTeamMember
        fields = ("user",)

    def validate_members(self, value):
        obj = self.context["obj"]
        value.remove(obj.captain)
        # TODO
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


class TeamSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="user.full_name")
    email = serializers.CharField(source="user.school_email")
    is_captain = serializers.SerializerMethodField()
    avatar = serializers.URLField(source="user.avatar.image.url")

    class Meta:
        model = TournamentTeamMember
        fields = ("pk", "full_name", "email", "is_captain", "avatar")

    def get_is_captain(self, obj):
        return obj.team.captain == self.context["request"].user

from rest_framework import serializers

from tournaments.models import Tournament, TournamentTeam


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
        fields = ("members",)

    def validate_members(self, value):
        team_captain = self.context["obj"].captain
        if team_captain not in value:
            value.append(team_captain)
        return value

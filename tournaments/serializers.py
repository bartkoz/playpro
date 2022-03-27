from rest_framework import serializers

from tournaments.models import Tournament, TournamentTeam
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

        model = TournamentTeam
        fields = ("members",)

    def validate_members(self, value):
        obj = self.context["obj"]
        if obj.captain not in value:
            value.append(obj.captain)
        if obj.tournament.team_size < len(value):
            raise serializers.ValidationError(
                _(
                    f"Team can oan consist of maximum of {obj.tournament.team_size} teammates."
                )
            )
        if any(
            [
                x != self.context["request"].user
                for x in User.objects.filter(pk__in=[x.pk for x in value])
                .prefetch_related("school")
                .values_list("school_id", flat=True)
            ]
        ):
            raise serializers.ValidationError(
                _("You may only invite people from your schoool.")
            )
        return value

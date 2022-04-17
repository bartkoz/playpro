import factory
from faker import Faker

from tournaments.models import (
    Tournament,
    TournamentTeam,
    TournamentTeamMember,
    TournamentGroup,
)
from users.factories import UserFactory
from users.models import School


class TournamentTeamFactory(factory.django.DjangoModelFactory):
    school = School.objects.order_by("?").first()
    tournament = Tournament.objects.order_by("?").first()
    name = Faker(
        [
            "en_US",
        ]
    ).sentence(nb_words=3)
    tournament_joined = True
    captain = factory.SubFactory(UserFactory)

    class Meta:
        model = TournamentTeam


class TournamentTeamMemberFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TournamentTeamFactory)

    class Meta:
        model = TournamentTeamMember


class TournamentGroupFactory(factory.django.DjangoModelFactory):
    tournament = Tournament.objects.order_by("?").first()

    class Meta:
        model = TournamentGroup

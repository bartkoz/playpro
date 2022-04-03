import itertools
import random

from django.db.models import Count
from django.utils import timezone

from tournaments.models import Tournament, TournamentTeam, TournamentMatch


def get_division_value(team_count):
    if team_count >= 64:
        return 8
    elif team_count >= 32:
        return 8
    else:
        return 4


def build_chunks(chunk_size, data):
    final_chunks = []
    remainder = len(data) % chunk_size
    equal_part = len(data) - remainder
    chunks_count = int(equal_part / chunk_size + 1)
    for _ in range(chunks_count):
        final_chunks.append([])
    for _ in range(chunks_count):
        for chunk in final_chunks:
            try:
                chunk.append(data.pop(0))
            except IndexError:
                break
    return final_chunks


def create_tournament_groups_or_ladder():

    for tournament in (
        Tournament.objects.annotate(groups_count=Count("tournament_groups"))
        .filter(registration_close_date__lte=timezone.now(), groups_count=0)
        .values_list("pk", flat=True)
    ):
        team_size = tournament.team_size
        qs = TournamentTeam.objects.annotate(team_size=Count("team_members")).filter(
            tournament_id=tournament, team_size=team_size
        )
        randomized_qs = list(qs)
        random.shuffle(randomized_qs)
        if qs.count() <= 16:
            chunks = build_chunks(2, randomized_qs)
            tournament.playoff_array = chunks
            tournament.save()
            for chunk in chunks:
                obj = TournamentMatch.objects.create(
                    tournament=tournament,
                    stage=TournamentMatch.StageChoices.PLAYOFF,
                    round_number=1,
                )
                for team in chunk:
                    obj.add(team)
                    obj.save()
        else:
            group_size = get_division_value(qs.count())
            chunks = build_chunks(group_size, randomized_qs)
            for chunk in chunks:
                team_pairs = list(itertools.combinations(chunk, 2))
                for team_pair in team_pairs:
                    obj = TournamentMatch.objects.create(
                        tournament=tournament, stage=TournamentMatch.StageChoices.GROUP
                    )
                    for team in team_pair:
                        obj.add(team)
                        obj.save()

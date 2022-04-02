from django.db.models.signals import post_save
from django.dispatch import receiver

from tournaments.models import TournamentMatch
from tournaments.tasks import build_chunks


@receiver(post_save, sender=TournamentMatch)
def playoff_handler(sender, instance, **kwargs):
    # round_nr: games_until_stage_finished
    rounds_map = {1: 8,
                  2: 4,
                  3: 2}
    if instance.tournament.tournament_matches.filter(winner__isnull=False).count() == rounds_map[instance.round_number]:
        winners = []
        for pair in instance.tournament.playoff_array:
            for team in pair:
                match = team.matches.get(tournament=instance.tournament, round_number=instance.round_number)
                if match.winner == team:
                    winners.append(team)
        chunks = build_chunks(2, winners)
        for chunk in chunks:
            obj = TournamentMatch.objects.create(
                tournament=instance.tournament, stage=TournamentMatch.StageChoices.GROUP
            )
            for team in chunk:
                obj.add(team)
                obj.save()

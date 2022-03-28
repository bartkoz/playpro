# Generated by Django 4.0.3 on 2022-03-28 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tournament",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("registration_open_date", models.DateTimeField()),
                ("registration_close_date", models.DateTimeField()),
                ("registration_check_in_date", models.DateTimeField()),
                ("name", models.CharField(max_length=255)),
                ("logo", models.ImageField(upload_to="")),
                ("team_size", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="TournamentPlatform",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="TournamentTeam",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("group_score", models.IntegerField(default=0)),
                ("wins", models.IntegerField(default=0)),
                ("losses", models.IntegerField(default=0)),
                (
                    "captain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="users.school"
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="tournaments.tournament",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TournamentTeamMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("invitation_accepted", models.BooleanField(null=True)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_members",
                        to="tournaments.tournamentteam",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TournamentMatch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[("playoff", "Playoff"), ("group", "Group")],
                        max_length=20,
                    ),
                ),
                ("match_start", models.DateTimeField()),
                ("is_contested", models.BooleanField(blank=True, null=True)),
                (
                    "contest_screenshot",
                    models.ImageField(blank=True, null=True, upload_to=""),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="tournaments.tournament",
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="tournaments.tournamentteam",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TournamentGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("teams", models.ManyToManyField(to="tournaments.tournamentteam")),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="tournaments.tournament",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tournament",
            name="platforms",
            field=models.ManyToManyField(to="tournaments.tournamentplatform"),
        ),
    ]

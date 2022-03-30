# Generated by Django 4.0.3 on 2022-03-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentmatch",
            name="contestants",
            field=models.ManyToManyField(
                related_name="matches", to="tournaments.tournamentteam"
            ),
        ),
    ]
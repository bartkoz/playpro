# Generated by Django 4.0.3 on 2022-05-09 10:05

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import tournaments.models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0004_gamertagchoice_tournamentgame_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentmatch",
            name="result_submitted",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(), blank=True, null=True, size=2
            ),
        ),
    ]
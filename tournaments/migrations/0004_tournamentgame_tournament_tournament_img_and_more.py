# Generated by Django 4.0.3 on 2022-04-22 16:01

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import tournaments.models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0003_alter_tournament_logo_alter_tournament_playoff_array_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TournamentGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='tournament',
            name='tournament_img',
            field=models.ImageField(null=True, upload_to='tournaments/b1615338-9926-47dc-b655-efd204d2efe2'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='logo',
            field=models.ImageField(upload_to='tournaments/a0e2bf81-6426-462c-b2b8-3e16ce875246'),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='chat_channel',
            field=models.CharField(default=tournaments.models.create_match_chat, max_length=15),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='contest_screenshot',
            field=models.ImageField(blank=True, null=True, upload_to='tournament_result/8ff85d0c-f58b-4548-917b-46f56d9cf70d'),
        ),
        migrations.CreateModel(
            name='TournamentGamePlatformMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gamer_tag_types', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('epic_games_id', 'epic_games_id'), ('ea_games_id', 'ea_games_id'), ('ps_network_id', 'ps_network_id'), ('riot_id', 'riot_id'), ('xbox_id', 'xbox_id')], max_length=255), size=None)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tournaments.tournamentgame')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tournaments.tournamentplatform')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='tournament',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='tournaments.tournamentgame'),
        ),
    ]

# Generated by Django 4.0.3 on 2022-04-22 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0005_remove_tournamentgameplatformmap_gamer_tag_types_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamerTagChoice',
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
        migrations.AlterField(
            model_name='tournament',
            name='logo',
            field=models.ImageField(upload_to='tournaments/83f0b9ff-5c73-49e6-8e9b-65bbbf63068c'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='tournament_img',
            field=models.ImageField(null=True, upload_to='tournaments/6d455460-1c04-4cce-9d4d-dafe62b20f32'),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='contest_screenshot',
            field=models.ImageField(blank=True, null=True, upload_to='tournament_result/1ecb9760-c712-4f22-ad11-21add78073c9'),
        ),
        migrations.AddField(
            model_name='tournamentgameplatformmap',
            name='gamer_tag_types',
            field=models.ManyToManyField(to='tournaments.gamertagchoice'),
        ),
    ]

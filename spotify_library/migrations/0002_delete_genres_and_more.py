# Generated by Django 5.0.4 on 2024-05-07 11:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_library', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(
            name='Genres',
        ),
        migrations.RemoveConstraint(
            model_name='usertracks',
            name='unique_track_uris_for_user',
        ),
        migrations.AddConstraint(
            model_name='usertracks',
            constraint=models.UniqueConstraint(fields=('user', 'track_uri', 'playlist_id_or_saved_song'), name='unique_track_uris_for_user'),
        ),
    ]

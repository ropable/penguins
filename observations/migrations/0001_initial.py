# Generated by Django 4.2.14 on 2024-07-31 02:42

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('camera_key', models.CharField(default='', help_text='Space-separated list of keys to match video recordings', max_length=100)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='The date of the recording.')),
                ('file', models.FileField(upload_to='videos')),
                ('start_time', models.TimeField(help_text='The start time of the recording.')),
                ('end_time', models.TimeField(help_text='The end time of the recording (usually 1h after start).')),
                ('views', models.PositiveSmallIntegerField(default=0)),
                ('mark_complete', models.BooleanField(default=False, help_text='Has this been viewed in its entirety by a reviewer?')),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.camera')),
                ('completed_by', models.ManyToManyField(related_name='videos_seen', to=settings.AUTH_USER_MODEL, verbose_name='Users who have seen this video')),
            ],
            options={
                'ordering': ['-date', '-start_time'],
            },
        ),
        migrations.CreateModel(
            name='PenguinObservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(help_text='The date on which the observation is noted')),
                ('position', models.FloatField(default=0, help_text='Position in video (seconds from start)', null=True, verbose_name='Position (s)')),
                ('seen', models.PositiveSmallIntegerField(help_text='The count of penguins seen in this observation.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='count')),
                ('comments', models.TextField(blank=True, null=True)),
                ('raining', models.BooleanField(default=False, help_text='Was it raining at the time of the observation?')),
                ('validated', models.BooleanField(default=True, verbose_name='Confirmed')),
                ('observer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='observations', to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='observations.video')),
            ],
        ),
    ]

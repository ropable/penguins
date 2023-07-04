# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.contrib.gis.db.models.fields
import django.contrib.auth.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PenguinUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(verbose_name='username', max_length=30, unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], error_messages={'unique': 'A user with that username already exists.'})),
                ('first_name', models.CharField(verbose_name='first name', max_length=30, blank=True)),
                ('last_name', models.CharField(verbose_name='last name', max_length=30, blank=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=254, blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('camera_key', models.CharField(max_length=100, default='')),
                ('ip_address', models.CharField(max_length=100, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PenguinCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('comments', models.TextField(blank=True, null=True)),
                ('civil_twilight', models.DateTimeField(blank=True, null=True)),
                ('sub_fifteen', models.DecimalField(verbose_name='-15-0', default=0, max_digits=5, decimal_places=2)),
                ('zero_to_fifteen', models.DecimalField(verbose_name='0-15', default=0, max_digits=5, decimal_places=2)),
                ('fifteen_to_thirty', models.DecimalField(verbose_name='15-30', default=0, max_digits=5, decimal_places=2)),
                ('thirty_to_fourty_five', models.DecimalField(verbose_name='30-45', default=0, max_digits=5, decimal_places=2)),
                ('fourty_five_to_sixty', models.DecimalField(verbose_name='45-60', default=0, max_digits=5, decimal_places=2)),
                ('sixty_to_seventy_five', models.DecimalField(verbose_name='60-75', default=0, max_digits=5, decimal_places=2)),
                ('seventy_five_to_ninety', models.DecimalField(verbose_name='75-90', default=0, max_digits=5, decimal_places=2)),
                ('ninety_to_one_oh_five', models.DecimalField(verbose_name='90-105', default=0, max_digits=5, decimal_places=2)),
                ('one_oh_five_to_one_twenty', models.DecimalField(verbose_name='105-120', default=0, max_digits=5, decimal_places=2)),
                ('total_penguins', models.DecimalField(verbose_name='total penguins', default=0, max_digits=5, decimal_places=2)),
                ('outlier', models.DecimalField(verbose_name='outlying times', default=0, max_digits=5, decimal_places=2)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='PenguinObservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('seen', models.PositiveSmallIntegerField(verbose_name='count', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('comments', models.TextField(blank=True, null=True)),
                ('wind_direction', models.PositiveSmallIntegerField(verbose_name='Wind direction', blank=True, null=True, choices=[(1, 'N'), (2, 'NNW'), (3, 'NW'), (4, 'WNW'), (5, 'W'), (6, 'WSW'), (7, 'SW'), (8, 'SSW'), (9, 'S'), (10, 'SSE'), (11, 'SE'), (12, 'ESE'), (13, 'E'), (14, 'ENE'), (15, 'NE'), (16, 'NNE')])),
                ('wind_speed', models.DecimalField(verbose_name='Wind speed (km/h)', blank=True, null=True, max_digits=4, decimal_places=1)),
                ('wave_direction', models.PositiveSmallIntegerField(verbose_name='Wave direction', blank=True, null=True, choices=[(1, 'N'), (2, 'NNW'), (3, 'NW'), (4, 'WNW'), (5, 'W'), (6, 'WSW'), (7, 'SW'), (8, 'SSW'), (9, 'S'), (10, 'SSE'), (11, 'SE'), (12, 'ESE'), (13, 'E'), (14, 'ENE'), (15, 'NE'), (16, 'NNE')])),
                ('wave_height', models.DecimalField(verbose_name='Wave height (m)', blank=True, null=True, max_digits=4, decimal_places=1)),
                ('wave_period', models.PositiveSmallIntegerField(verbose_name='Wave period (s)', blank=True, null=True)),
                ('moon_phase', models.PositiveSmallIntegerField(verbose_name='Moon phase', blank=True, null=True, choices=[(1, 'Full'), (2, 'First quarter'), (3, 'Half'), (4, 'Third quarter'), (5, 'New')])),
                ('raining', models.BooleanField(verbose_name='Raining?', default=False, help_text='Was it raining at the time of the observation?')),
                ('position', models.FloatField(verbose_name='Position in video', null=True, default=0)),
                ('validated', models.BooleanField(verbose_name='Confirmed', default=True)),
                ('camera', models.ForeignKey(blank=True, null=True, to='observations.Camera')),
                ('observer', models.ForeignKey(related_name='observations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PenguinVideoObservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True, default='')),
                ('date', models.DateField(verbose_name='Date', help_text='The date of the recording.')),
                ('file', models.FileField(upload_to='videos')),
                ('start_time', models.TimeField(verbose_name='Start time', help_text='The start time of the recording.')),
                ('end_time', models.TimeField(verbose_name='End time', help_text='The end time of the recording (usually 1h after start).')),
                ('views', models.IntegerField(default=0)),
                ('mark_complete', models.BooleanField(default=False, help_text='Has this been viewed in its entirety by a reviewer')),
                ('camera', models.ForeignKey(to='observations.Camera')),
                ('completed_by', models.ManyToManyField(verbose_name='Users who have seen this video', related_name='videos_seen', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='penguinvideoobservation',
            name='video',
            field=models.ForeignKey(to='observations.Video'),
        ),
        migrations.AddField(
            model_name='penguinobservation',
            name='site',
            field=models.ForeignKey(to='observations.Site'),
        ),
        migrations.AddField(
            model_name='penguinobservation',
            name='video',
            field=models.ForeignKey(verbose_name='Video filename', null=True, default=None, to='observations.Video'),
        ),
        migrations.AddField(
            model_name='penguincount',
            name='site',
            field=models.ForeignKey(to='observations.Site'),
        ),
        migrations.AddField(
            model_name='camera',
            name='site',
            field=models.ForeignKey(blank=True, null=True, to='observations.Site'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(null=True, blank=True, max_length=50)),
                ('file_field', models.FileField(null=True, blank=True, upload_to='files')),
                ('thumbnail', models.ImageField(null=True, blank=True, upload_to='files')),
                ('uploader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(verbose_name='Titel', max_length=100)),
                ('description', models.CharField(null=True, blank=True, verbose_name='Beskrivning', max_length=4000)),
                ('facebook_publish', models.BooleanField(verbose_name='Facebook', default=False)),
                ('publish_date', models.DateField(null=True, blank=True, verbose_name='Publiceringsdatum')),
                ('internal_notes', models.CharField(null=True, blank=True, verbose_name='Anteckningar', max_length=4000)),
                ('published', models.BooleanField(default=False)),
                ('email_sent', models.BooleanField(default=False)),
                ('documents', models.ManyToManyField(null=True, blank=True, to='planner.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('initial_description', models.TextField(max_length=4000)),
                ('image', models.ImageField(null=True, blank=True, upload_to='images')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('attending', models.CharField(max_length=10, default='null')),
                ('email_sent', models.BooleanField(default=False)),
                ('last_email_sent', models.DateField(null=True, blank=True)),
                ('event', models.ForeignKey(to='planner.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('token', models.CharField(max_length=250)),
                ('creation_date', models.DateField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='participation',
            name='role',
            field=models.ForeignKey(to='planner.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventtype',
            name='roles',
            field=models.ManyToManyField(to='planner.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='event',
            field=models.ForeignKey(to='planner.Occurrence', verbose_name='Tidpunkt', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(to='planner.EventType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='planner.Participation'),
            preserve_default=True,
        ),
    ]

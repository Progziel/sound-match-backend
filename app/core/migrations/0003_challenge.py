# Generated by Django 3.2.25 on 2025-04-24 04:55

import core.models.challenge
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_soundpack'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sound_url', models.URLField()),
                ('levels', models.JSONField(default=list, validators=[core.models.challenge.validate_levels])),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_challenges', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

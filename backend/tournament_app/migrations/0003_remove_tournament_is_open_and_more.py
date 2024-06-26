# Generated by Django 5.0 on 2024-02-29 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament_app', '0002_alter_registrationtournament_alias'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='is_open',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='max_participants',
        ),
        migrations.AlterField(
            model_name='registrationtournament',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]

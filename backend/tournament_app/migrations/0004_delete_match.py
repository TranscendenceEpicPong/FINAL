# Generated by Django 5.0 on 2024-03-08 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament_app', '0003_remove_tournament_is_open_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Match',
        ),
    ]
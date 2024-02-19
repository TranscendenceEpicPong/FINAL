# Generated by Django 4.2.10 on 2024-02-13 00:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='player2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opponents_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
# Generated by Django 4.2.10 on 2024-02-09 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blocks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blocks',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blocks',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks_of_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
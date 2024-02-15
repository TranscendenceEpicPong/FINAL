from django.db import models
from core.models import EpicPongUser as User

# Create your models here.
class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_of_user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_user')
    status = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'friend']
        db_table = 'friends'
        managed = True
        verbose_name = 'Friend'
        verbose_name_plural = 'Friends'
from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProject


class Message(models.Model):
    topic = models.ForeignKey(Topic)
    publisher = models.ForeignKey(UserProject)
    content = models.CharField(max_length=90,
                               verbose_name='内容')
    created_time = models.DateTimeField(auto_now_add=True)
    parent_message = models.IntegerField(default=0)

    class Meta:
        db_table = 'message'

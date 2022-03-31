from django.db import models

from playpro.abstract import TimestampAbstractModel
from users.models import User


class Notification(TimestampAbstractModel, models.Model):

    meta = models.JSONField(default=dict())
    read = models.BooleanField(default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

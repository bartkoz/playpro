from django.db import models


class TimestampAbstractModel(models.Model):
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        abstract = True

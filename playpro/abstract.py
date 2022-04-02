from django.db import models


class CustomBigIntegerAuto(models.BigAutoField):

    def get_internal_type(self):
        return "BigIntegerField"

    def db_type(self, connection):
        db_type_format = 'BIGINT DEFAULT public.next_id()'

        return db_type_format


class TimestampAbstractModel(models.Model):
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)
    # id = CustomBigIntegerAuto(primary_key=True, )

    class Meta:
        abstract = True

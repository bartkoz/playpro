from django.db.models.signals import post_save
from django.dispatch import receiver


# @receiver(post_save, sender=Comment)
# def increment_comments_count(sender, instance, **kwargs):
#     pass
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse

from notifications.enums import NotificationTypes
from notifications.models import Notification
from notifications.signals import invitation_revoked, invitation_created


# @receiver(invitation_created)
def notify_user_about_new_invitation(instance, **kwargs):
    channel_layer = get_channel_layer()
    url = "{}{}".format(
        settings.BASE_URL,
        reverse(
            "tournaments:tournament_invitations-detail", kwargs={"pk": instance.pk}
        ),
    )
    content = "You have been invited to the team {} in {} tournament.".format(
        instance.team.name, instance.team.tournament.name
    )
    async_to_sync(channel_layer.group_send)(
        instance.user.notifications_channel,
        {
            "type": "notification",
            "message": {
                "url": url,
                "content": content,
                "read": False,
            },
        },
    )
    Notification.objects.create(
        user=instance.user,
        meta={
            "type": NotificationTypes.INVITATION.value,
            "obj_pk": instance.pk,
            "tournament_name": instance.team.tournament.name,
            "team_name": instance.team.name,
        },
    )


# @receiver(invitation_revoked)
def notify_user_about_invitation_revoked(instance, **kwargs):
    channel_layer = get_channel_layer()
    message = (
        "Your invitation to the team {} in {} tournament has been revoked.".format(
            instance.team.name, instance.team.tournament.name
        )
    )
    async_to_sync(channel_layer.group_send)(
        instance.user.notifications_channel,
        {
            "type": "notification",
            "message": {
                "url": "",
                "message": message,
                "read": False,
            },
        },
    )
    Notification.objects.create(
        user=instance.user,
        meta={
            "type": NotificationTypes.INVITATION_REVOKE.value,
            "tournament_name": instance.team.tournament.name,
            "team_name": instance.team.name,
        },
    )


def notify_captain_invitation_denied(instance):
    # channel_layer = get_channel_layer()
    message = "{} has denied your invitation to team {} in tournament {}".format(
        instance.user.nickname, instance.team.name, instance.team.tournament.name
    )
    # async_to_sync(channel_layer.group_send)(
    #     instance.user.notifications_channel,
    #     {
    #         "type": "notification",
    #         "message": {
    #             "url": "",
    #             "message": message,
    #             "read": False,
    #         },
    #     },
    # )
    Notification.objects.create(
        user=instance.user,
        meta={
            "type": NotificationTypes.INVITATION_REFUSED.value,
            "tournament_name": instance.team.tournament.name,
            "team_name": instance.team.name,
            "invited_user": instance.user.nickname,
        },
    )

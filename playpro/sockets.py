import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from jwt import decode as jwt_decode, ExpiredSignatureError
from django.conf import settings
from urllib.parse import parse_qs

from notifications.enums import NotificationTypes
from notifications.models import Notification
from tournaments.models import TournamentMatch
from users.models import User


def get_user(scope):
    try:
        token = parse_qs(scope["query_string"].decode("utf8")).get("token")[0]
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(pk=decoded_data.get("user_id"))
    except (User.DoesNotExist, ExpiredSignatureError):
        return AnonymousUser()


def check_match_lobby_eligibility(user, room_channel):
    if user.pk in TournamentMatch.objects.filter(
        chat_channel=room_channel
    ).prefetch_related("contestants__team_members").values_list(
        "contestants__team_members__user__pk", flat=True
    ):
        return True
    return False


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_group_name = uuid.uuid4()
        self.user = get_user(self.scope)
        if self.user.is_authenticated:
            self.channel_group_name = self.user.notifications_channel
            self.accept()
            async_to_sync(self.channel_layer.group_add)(
                self.channel_group_name, self.channel_name
            )
            self.send_initial_msg()
        else:
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name, {"type": "notification", "message": message}
        )

    def notification(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))

    def __build_single_notification(self, obj):
        if obj.meta.get("type") == NotificationTypes.INVITATION.value:
            msg = {
                "type": "notification",
                "message": {
                    "url": f"{settings.BASE_URL}"
                    f"{reverse('tournaments:tournament_invitations-detail', kwargs={'pk': obj.meta['obj_pk']})}",
                    "content": f"You have been invited to the team "
                    f"{obj.meta['team_name']} in {obj.meta['tournament_name']} tournament.",
                    "read": obj.read,
                },
            }
        elif obj.meta.get("type") == NotificationTypes.INVITATION_REVOKE.value:
            msg = {
                "type": "notification",
                "message": {
                    "url": "",
                    "message": "{} has denied your invitation to team {} in tournament {}".format(
                        obj.meta["invited_user"],
                        obj.meta["team_name"],
                        obj.meta["tournament_name"],
                    ),
                },
            }
        else:
            msg = {
                "type": "notification",
                "message": {
                    "url": "",
                    "message": f"Your invitation to the team {obj.meta['team_name']} "
                    f"in {obj.meta['tournament_name']} tournament has been revoked.",
                    "read": obj.read,
                },
            }
        return msg

    def send_initial_msg(self):
        for notification in Notification.objects.filter(user=self.user).only(
            "meta", "read"
        ):
            async_to_sync(self.channel_layer.group_send)(
                self.channel_group_name, self.__build_single_notification(notification)
            )


class PreMatchChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = get_user(self.scope)
        if self.user.is_authenticated:
            channel_name = self.scope["path"].split("/")[-2]
            if check_match_lobby_eligibility(self.user, channel_name):
                team = TournamentMatch.objects.filter(
                    chat_channel=channel_name, contestants__team_members__user=self.user
                ).first()
                self.channel_group_name = channel_name
                if team:
                    self.team = team.name
                else:
                    self.close()
                self.accept()
                async_to_sync(self.channel_layer.group_add)(
                    self.channel_group_name, self.channel_name
                )

            else:
                self.close()
        else:
            self.close()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                "type": "chat_message",
                "team": self.team,
                "username": self.user.nickname,
                "message": message,
            },
        )

    def notification(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))

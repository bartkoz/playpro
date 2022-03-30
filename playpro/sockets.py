import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs

from users.models import User


def get_user(scope):
    try:
        token = parse_qs(scope["query_string"].decode("utf8")).get("token")[0]
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(pk=decoded_data.get("user_id"))
    except User.DoesNotExist:
        return AnonymousUser()


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = get_user(self.scope)
        if self.user.is_authenticated:
            self.channel_group_name = self.user.notifications_channel
            self.accept()
        else:
            self.close()
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name, self.channel_name
        )

        self.accept()

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


# message = 'asdasdd'
# channel_layer = get_channel_layer()
# async_to_sync(channel_layer.group_send)(
#     'test',
#     {'type': 'notification', 'message': message}
# )

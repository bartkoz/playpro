import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['name']
        self.channel_group_name = 'test'
        self.user = self.scope['user']
        # if self.user.is_authenticated:
        #     self.accept()
        # else:
        #     self.close()
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'notification',
                'message': message
            }
        )

    def notification(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


# message = 'asdasdd'
# channel_layer = get_channel_layer()
# async_to_sync(channel_layer.group_send)(
#     'test',
#     {'type': 'notification', 'message': message}
# )
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Group, MyUser
from datingAPI.appProcessing import get_download_link_from_file
from .serializers import MessageSerializer, MessageSerializerWrite
from django.contrib.auth.models import AnonymousUser


def message_to_json(message):
    try:
        result = {
            'group_id': str(message.group_id.id),
            'creator': message.creator.username,
            'content': message.content,
            'created_at': str(message.created_at),
        }
        if message.file_url is not None:
            result['file_url'] = get_download_link_from_file(message.file_url)  # TODO Check Here
        if message.replying_to is not None:
            result['replying_to'] = message.replying_to.username
    except:
        result = {}

    return result


def messages_to_json(messages):
    result = []
    for message in messages:
        result.append(message_to_json(message))
    return result


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # The user gets in the chat page so it means he/she is looking.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.chat_id = int(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        self.group_obj = Group.objects.get(id=self.chat_id)
        if self.user is not AnonymousUser() and self.user in self.group_obj.users.all():

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        # Leave the websocket and the chat page not deleting or anything. ( User is not looking at the chat )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def fetch_messages(self):
        try:
            # Get the latest 19 messages by date
            content = {
                'command': 'messages',
                'messages': messages_to_json(
                    Message.objects.filter(
                        group_id=Group.objects.get(id=self.chat_id)
                    ).order_by('-created_at')[19]
                ),
            }
        except:
            content = {}
        # Send the message to the user that requested this only not the group.
        self.send_socket_message(content)  # To the requester only

    def new_message(self, j_data):
        data = j_data['message']
        # For the file. We'll work on it later.
        message = None
        try:
            replying_to = None
            try:
                replying_to = MyUser.objects.get(username=str(data['replying_to'])) if 'replying_to' in data else None
            except MyUser.DoesNotExist:
                pass
            # We will upload the file from http and then from fetch we provide the download link.
            file_url = str(data['file_url']) if 'file_url' in data else None
            data['replying_to'] = replying_to
            data['group_id'] = self.group_obj
            data['creator'] = self.user
            data['file_url'] = file_url
            serializer = MessageSerializerWrite(data=data)
            if serializer.is_valid():
                serializer.save()
                message = serializer.Meta.model
        except:
            pass

        # Send message to the whole group.
        if message:
            return self.send_socket_message_group({
                'command': 'new_message',
                'message': MessageSerializer(message, many=False).data
            })
        else:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    commands = {"fetch_messages": fetch_messages,
                "new_message": new_message,
                }

    def receive(self, text_data):  # A new message/request from websocket. Can be message or anything.
        data = json.loads(text_data)
        try:
            self.commands[data["command"]](data)
        except:
            pass

    def send_socket_message_group(self, message):  # Send socket message to the whole group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_socket_message(self, message):  # Send socket message to the requester only
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):  # Don't touch this. Default thing
        message = event['message']
        self.send(text_data=json.dumps(message))

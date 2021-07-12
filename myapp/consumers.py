import json
# from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Group, MyUser
from .serializers import MessageSerializer, MessageSerializerWrite
from django.contrib.auth.models import AnonymousUser


def message_to_json(message):
    try:
        result = {
            'group_id': str(message.group_id.id),
            'creator': message.creator.username,
            'content': message.content,
            'created_at': str(message.created_at),
            'file_url': message.file_url  # Check here
        }
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


class ChatConsumer(AsyncWebsocketConsumer):  # TODO: Check if user is looking at the chat
    async def connect(self):
        # The user gets in the chat page so it means he/she is looking.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.chat_id = int(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        self.group_obj = Group.objects.get(id=self.chat_id)
        group_users = self.group_obj.users.all()
        if group_users.count() == 2:  # me and another user
            for group_user in group_users:
                if not group_user == self.user:
                    if self.user not in group_user.block_list.all():
                        if self.user is not AnonymousUser() and self.user in self.group_obj.users.all():
                            # Connect to the group
                            await self.channel_layer.group_add(
                                self.room_group_name,
                                self.channel_name
                            )

                            await self.accept()
        else:
            if self.user is not AnonymousUser() and self.user in self.group_obj.users.all():
                # Connect to the group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                await self.accept()

    async def disconnect(self, close_code):
        # Leave the websocket and the chat page not deleting or anything. ( User is not looking at the chat )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def fetch_messages(self):
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
        await self.send_socket_message(content)  # To the requester only

    async def new_message(self, j_data):
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
            data['file_url'] = str(data['file_url']) if 'file_url' in data else ""
            data['replying_to'] = replying_to
            data['group_id'] = self.group_obj
            data['creator'] = self.user
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
                'message': {
                    MessageSerializer(message, many=False).data
                }
            })
        else:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    commands = {"fetch_messages": fetch_messages,
                "new_message": new_message,
                }

    async def receive(self, text_data):  # A new message/request from websocket. Can be message or anything.
        data = json.loads(text_data)
        try:
            await self.commands[data["command"]](data)
        except:
            pass

    async def send_socket_message_group(self, message):  # Send socket message to the whole group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_socket_message(self, message):  # Send socket message to the requester only
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):  # Don't touch this. Default thing
        message = event['message']
        await self.send(text_data=json.dumps(message))

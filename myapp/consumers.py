import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from userManagement.models import MyUser
from .models import Group, Message
from .serializers import MessageSerializer, MessageSerializerMain
from django.contrib.auth.models import AnonymousUser
import asyncio


class ChatConsumer(AsyncConsumer):
    @database_sync_to_async
    def get_messages(self):
        count = Message.objects.filter(group_id=self.group_obj).count()
        if count >= 20:
            return Message.objects.filter(
                group_id=self.group_obj
            ).order_by('-created_at')[:19]
        return Message.objects.filter(
            group_id=self.group_obj
        ).order_by('-created_at')

    @database_sync_to_async
    def create_message(self, data):
        msg = Message()
        msg.creator = data['creator']
        msg.content = data['content']
        msg.file_url = data['file_url']
        if data['replying_to'] is not None:
            msg.replying_to = data['replying_to']
        msg.group_id = data['group_id']
        msg.save()
        return msg

    @database_sync_to_async
    def serialize_message(self, msgs):
        return MessageSerializer(msgs, many=True).data

    @database_sync_to_async
    def serialize_message_2(self, msgs):
        return MessageSerializer(msgs, many=False).data

    async def fetch_messages(self):
        #try:
            # Get the latest 19 messages by date
        msgs = await self.get_messages()
        if msgs is not None:
            content = {
                'type': 'websocket.send',
                'text': json.dumps({
                    "messages": await self.serialize_message(msgs)
                })
            }
        else:
            content = {
                'type': 'websocket.send',
                'text': json.dumps({
                    'messages': []
                })
            }
        #except:
            #
        # Send the message to the user that requested this only not the group.
        await self.send_socket_message(content)  # To the requester only

    async def new_message(self, j_data):
        data = j_data['message']
        # For the file. We'll work on it later.
        #try:
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
        message = await self.create_message(data)
        #except:
            #pass
        # Send message to the whole group.

        return await self.send_socket_message_group({'message': await self.serialize_message_2(message)})

    async def online_command(self):
        return await self.send_socket_message_group({"Online": self.user.username})

    async def typing_command(self):
        return await self.send_socket_message_group({"Typing": self.user.username})

    @database_sync_to_async
    def get_count(self):
        return self.group_obj.users.all().count()

    @database_sync_to_async
    def check_me(self):
        if self.user in self.group_obj.users.all():
            return True

    @database_sync_to_async
    def check_block(self):
        for group_user in self.group_obj.users.all():
            if not group_user == self.user:
                if self.user in group_user.block_list.all():
                    return False
        return True

    async def websocket_connect(self, message):
        self.group_name = self.scope['url_route']['kwargs']['chat_id']
        self.chat_id = int(self.group_name)
        self.room_group_name = 'chat_%s' % self.group_name
        self.user = self.scope['user']
        self.group_obj = await self.get_chat()
        if self.group_obj is not None:
            group_users = self.group_obj.users.all()
            count = await self.get_count()
            if count == 2:  # me and another user
                if await self.check_block():
                    if self.user is not AnonymousUser() and await self.check_me() is True:
                        # Connect to the group
                        await self.channel_layer.group_add(
                            self.room_group_name,
                            self.channel_name
                        )  # Add to redis

                        await self.send({"type": "websocket.accept"})

                        await self.send_socket_message_group({"Online": self.user.username})
                        # await asyncio.sleep(5)
                        # await self.send({"type": "websocket.close"})
            else:
                if self.user is not AnonymousUser() and await self.check_me() is True:
                    # Connect to the group
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )

                    await self.send_socket_message_group({"Online": self.user.username})
                    # await asyncio.sleep(5)
                    # await self.send({"type": "websocket.close"})

    async def websocket_disconnect(self, message):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.send({"type": "websocket.close"})

    async def websocket_receive(self, message):
        data = json.loads(message['text'])
        if data['command'] == "fetch_messages":
            await self.fetch_messages()
        elif data['command'] == "new_message":
            await self.new_message(data)
        elif data['command'] == "chat_online":
            await self.online_command()
        elif data['command'] == "typing":
            await self.typing_command()
        #try:

        #except:
            #pass

    async def send_socket_message_group(self, message):  # Send socket message to the whole group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": json.dumps(message)
            }
        )

    async def send_socket_message(self, message):  # Send socket message to the requester only
        await self.send(message)

    async def chat_message(self, event):  # Don't touch this. Default thing used by type in group send
        await self.send(
            {
                "type": "websocket.send",
                "text": event["text"]
            }
        )

    @database_sync_to_async
    def get_chat(self):
        try:
            return Group.objects.get(id=self.chat_id)
        except Group.DoesNotExist:
            return None


class MainPageConsumer(AsyncConsumer):

    @database_sync_to_async
    def get_group_data(self):
        message_data = {}
        for group in self.user.chat_list.all():
            # message_data[f"{group.id}_{group.name}"] = MessageSerializer(Message.objects.filter(group_id=group).last(), many=False).data
            message_data[f"{group.id}_{group.name}"] = MessageSerializerMain(Message.objects.filter(group_id=group).last(), many=False).data
        return message_data

    @database_sync_to_async
    def get_group_data_special(self, last_message_id):
        message_data = {}
        for group in self.user.chat_list.all():
            message_data[f"{group.id}_{group.name}"] = MessageSerializerMain(Message.objects.filter(id__gt=last_message_id), many=True).data
            # message_data[f"{group.id}_{group.name}"] = MessageSerializerMain(Message.objects.filter(group_id=group).last(), many=False).data
        return message_data

    async def fetch_live_group(self, last_message_id=None):
        final_data = {
            'type': 'websocket.send',
            'text': json.dumps({
                "groups": await self.get_group_data() if last_message_id is None else await self.get_group_data_special(last_message_id)
            })
        }
        return await self.send_socket_message(final_data)

    async def websocket_connect(self, message):
        self.user = self.scope['user']
        if self.user is not AnonymousUser():
            await self.send({"type": "websocket.accept"})

    async def websocket_disconnect(self, message):
        await self.send({"type": "websocket.close"})

    async def websocket_receive(self, message):
        data = json.loads(message['text'])
        if data['command'] == "fetch_group_live":
            last_message_id = int(data['last_message_id'])
            await self.fetch_live_group()

    async def send_socket_message(self, message):  # Send socket message to the requester only
        await self.send(message)

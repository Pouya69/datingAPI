from rest_framework import serializers
from django.contrib.postgres.fields import ArrayField
from myapp.models import Message,Group,Date
from userManagement.models import MyUser


class GroupPictureSerializer(serializers.ModelSerializer):
    """For Serializing Picture"""
    class Meta:
        model = Group
        fields = ['group_img']


class DateSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Date
        fields = ['users']


class UserSerializerName(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = MyUser
        fields = ['username']


class GroupIdSerializerName(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Group
        fields = ['id']


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    replying_to = UserSerializerName(many=False, read_only=True)
    creator = UserSerializerName(many=False, read_only=True)
    group_id = GroupIdSerializerName(many=False, read_only=True)

    """For Serializing Message"""
    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializerWrite(serializers.ModelSerializer):
    replying_to = UserSerializerName(many=False, read_only=True)
    creator = UserSerializerName(many=False, read_only=True)
    group_id = GroupIdSerializerName(many=False, read_only=True)
    class Meta:
        model = Message
        fields = ['group_id', 'creator', 'replying_to', 'content', 'file_url']


class GroupSerializerGET(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['users', 'name', 'id_chat', 'last_message']


class GroupSerializerIdChat(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['id_chat']


class GroupSerializerAdmins(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['users', 'admins', 'owner', 'name', 'id_chat']

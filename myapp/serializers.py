from rest_framework import serializers
from django.contrib.postgres.fields import ArrayField
from myapp.models import Message, Group, Date
from userManagement.models import MyUser


class DateSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Date
        fields = ['users']


class GroupPictureSerializer(serializers.ModelSerializer):
    """For Serializing Picture"""
    class Meta:
        model = Group
        fields = ['group_img']


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


class GroupIdSerializerName2(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Group
        fields = ['name']


class MessageSerializerMain(serializers.ModelSerializer):
    group_id = GroupIdSerializerName(many=False, read_only=True)
    group_name = GroupIdSerializerName2(many=False, read_only=True)

    class Meta:
        model = Message
        fields = ['group_name', 'group_id', 'id', 'creator', 'created_at']


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    replying_to = UserSerializerName(many=False, read_only=True)
    creator = UserSerializerName(many=False, read_only=True)
    group_id = GroupIdSerializerName(many=False, read_only=True)
    group_name = GroupIdSerializerName2(many=False, read_only=True)

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
    users = UserSerializerName(many=True, read_only=True)
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['users', 'name', 'id_chat']


class GroupSerializerIdChat(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['id_chat']


class GroupSerializerAdmins(serializers.ModelSerializer):
    users = UserSerializerName(many=True, read_only=True)
    admins = UserSerializerName(many=True, read_only=True)
    owner = UserSerializerName(many=False, read_only=True)
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['users', 'admins', 'owner', 'name', 'id_chat']

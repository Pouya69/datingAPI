from rest_framework import serializers
from django.contrib.postgres.fields import ArrayField
from myapp.models import Message,Group,Date

 
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


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['group_id', 'creator', 'replying_to', 'content', 'file_url']


class GroupSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = Group
        fields = ['users', 'name', 'id_chat', 'last_message']

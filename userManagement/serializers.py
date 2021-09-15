from datetime import date

from .models import MyUser,VerifyLink
from rest_framework import serializers


class UserGetSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)
    age = serializers.SerializerMethodField('get_age')

    def get_age(self, user):
        return int((date.today() - user.date_of_birth).days / 365)

    class Meta:
        model = MyUser
        fields = ['age', 'gender', 'username', 'about', 'dating_with', 'feeling', 'interests', 'create_date', 'full_name']


class UserSerializerName(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = MyUser
        fields = ['username']


# User Serializer
class LoginUserSerializer(serializers.ModelSerializer):
    dating_with = UserSerializerName(many=False, read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)
    date_of_birth = serializers.DateField(format="%Y-%m-%d", required=False, read_only=True)
    """For Serializing User"""
    class Meta:
        model = MyUser
        fields = ['email', 'date_of_birth', 'profile_pic', 'account_type', 'gender', 'username', 'about', 'dating_with', 'feeling', 'interests', 'country', 'premium_days_left', 'private', 'create_date', 'full_name']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['username', 'about', 'private', 'full_name', 'country']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = '__all__'


class FriendsListSerializer(serializers.ModelSerializer):
    friends = UserSerializerName(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['friends']


class BlockListSerializer(serializers.ModelSerializer):
    block_list = UserSerializerName(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['block_list']


# User Serializer
class PictureSerializer(serializers.ModelSerializer):
    """For Serializing Picture"""
    class Meta:
        model = MyUser
        fields = ['profile_pic']


class VerifySerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = VerifyLink
        fields = ['__all__']

class VerifyUserSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = MyUser
        fields = ['email']

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = 'about'

class InterestsSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = MyUser
        fields = ['interests']

class FeelingsSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    class Meta:
        model = MyUser
        fields = ['feeling']

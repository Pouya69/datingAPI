from .models import MyUser,VerifyLink
from rest_framework import serializers


#Login Serializer
class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['age', 'gender', 'username', 'about', 'dating_with', 'feeling', 'interests']


# User Serializer
class LoginUserSerializer(serializers.ModelSerializer):
    """For Serializing User"""
    class Meta:
        model = MyUser
        fields = ['email', 'age', 'gender', 'username', 'about', 'dating_with', 'feeling', 'interests', 'premium_days_left']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'about']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = MyUser
        fields = '__all__'

class UserSerializerName(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = MyUser
        fields = ['username']


class FriendsListSerializer(serializers.ModelSerializer):
    friends = UserSerializerName(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['friends']

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

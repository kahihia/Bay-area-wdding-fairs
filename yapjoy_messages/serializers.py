from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Message


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.CharField(default='https://yapjoy-static.s3.amazonaws.com/media/media/tempPhoto.png',
                                        source='userprofile.image.url')
    profile_id = serializers.IntegerField(source='userprofile.id')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'get_full_name', 'profile_pic', 'profile_id')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'message', 'created_at')

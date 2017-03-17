from django.db import models
from django.contrib.auth.models import User


class EventTeam(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, blank=True)
    friends = models.ManyToManyField(User, null=True, blank=True, related_name='event_team_friends')
    event_date = models.DateField(null=True, blank=True)

    family_ref_code = models.CharField(max_length=100)
    vendor_ref_code = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s"%(self.name)

class FriendsChatList(models.Model):
    team = models.ForeignKey(EventTeam, null=True, blank=True)
    channel_id = models.CharField(max_length=50, null=True, blank=True)
    event = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='friends_chat_user')
    friend = models.ForeignKey(User, null=True, blank=True, related_name='friends_chat_friend')

    is_message_user = models.BooleanField(default=False)
    is_message_friend = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

from yapjoy_registration.models import UserProfile
class Messages(models.Model):
    team = models.ForeignKey(EventTeam, null=True, blank=True)
    friends_chat_list = models.ForeignKey("FriendsChatList", null=True, blank=True)
    channel_chat_list = models.ForeignKey("ChannelChatList", null=True, blank=True)
    message = models.CharField(max_length=500)
    sender = models.ForeignKey(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)

class ChannelChatList(models.Model):
    team = models.ForeignKey(EventTeam, null=True, blank=True)
    channel_id = models.CharField(max_length=50, null=True, blank=True)
    event = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='channel_chat_user')
    friend = models.ManyToManyField(User, null=True, blank=True, related_name='channel_chat_friend_list')

    is_message_user = models.BooleanField(default=False)
    is_message_friend = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# This code is triggered whenever a new user has been created and saved to the database

def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
post_save.connect(create_auth_token, sender=settings.AUTH_USER_MODEL)
from yapjoy_registration.models import id_generator

def create_event_team_token(sender, instance=None, created=False, **kwargs):
    if created:
        instance.family_ref_code = id_generator() + str(instance.id)
        instance.vendor_ref_code = id_generator() + str(instance.id)
        instance.save()
post_save.connect(create_event_team_token, sender=EventTeam)

def create_friends_token(sender, instance=None, created=False, **kwargs):
    if created:
        instance.channel_id = id_generator() + str(instance.id)
        instance.event = "new-comment"
        instance.save()
post_save.connect(create_friends_token, sender=FriendsChatList)

def create_channel_token(sender, instance=None, created=False, **kwargs):
    if created:
        instance.channel_id = id_generator() + str(instance.id)
        instance.event = "new-comment"
        instance.save()
post_save.connect(create_channel_token, sender=ChannelChatList)
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from yapjoy_registration.models import UserProfile


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='message_sender')
    receiver = models.ForeignKey(User, related_name='message_receiver')

    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=1500)

    receiver_read = models.BooleanField(default=False)
    sender_view = models.BooleanField(default=True)
    receiver_view = models.BooleanField(default=True)

    drafted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Feedback(models.Model):
    user = models.ForeignKey(User)
    subject = models.CharField(max_length=255)
    message = models.CharField(max_length=1500)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class ChatConnection(models.Model):

    TEXT = 'text'
    VIDEO = 'video'

    CHAT_TYPE_CHOICES = (
        (TEXT, 'Text'),
        (VIDEO, 'Video'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE,
                related_name='connection_sender_set')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                related_name='connection_receiver_set')
    session_id = models.TextField()
    archive_id = models.TextField(blank=True, null=True)
    chat_type = models.CharField(max_length=50,
                    choices=CHAT_TYPE_CHOICES)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class NotificationConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


from yapjoy_registration.commons import send_email
def create_notification_count(sender, instance, created, **kwargs):
    if created:
        userprofile = UserProfile.objects.get(user=instance.receiver)
        userprofile.message_count += 1
        send_email(instance.receiver.email, message="You have a new message from %s"%(instance.sender.get_full_name()), title="New message recieved", subject="You have recieved a new message on Yapjoy")
        userprofile.save()
post_save.connect(create_notification_count, sender=Message)

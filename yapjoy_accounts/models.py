from django.db import models
from django.contrib.auth.models import User
from yapjoy_registration.models import UserProfile
from django.db.models.signals import post_save
class CreditPackages(models.Model):
    SHOW = 'Show'
    HIDE = 'Hide'
    STATUS_CHOICES = {
        (SHOW, 'Show'),
        (HIDE, 'Hide'),
    }
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    credits = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "$%s - %s Credits"%(self.amount, self.credits)

class Transaction(models.Model):
    INCOMPLETE = "0"
    COMPLETED = "1"
    PENDING = "2"
    WIDRAWL = "3"
    STATUS_CHOICES = (
        (INCOMPLETE, 'Incomplete'),
        (COMPLETED, 'Completed'),
        (PENDING, 'Pending'),
        (WIDRAWL, 'Widrawl'),
    )
    user = models.ForeignKey(User)
    amount = models.FloatField()
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default=INCOMPLETE)
    transaction_id = models.CharField(max_length=1000)
    response = models.CharField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

class TransactionHistory(models.Model):
    user = models.ForeignKey(User)
    amount = models.IntegerField()
    event = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

class Notifications(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    message = models.CharField(max_length=500, null=True, blank=True)

    is_read = models.BooleanField(default=False)

    DEFAULT = "Default"
    TYPE_CHOICES = (
        (DEFAULT, 'Default'),
    )
    type = models.CharField(max_length=20,choices=TYPE_CHOICES, default=DEFAULT)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Packages(models.Model):
    amount = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

def create_notification_count(sender, instance, created, **kwargs):
    if created:
        profile = instance.userprofile
        profile.notification_count += 1
        profile.save()
post_save.connect(create_notification_count, sender=Notifications)
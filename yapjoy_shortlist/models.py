from django.db import models
from django.contrib.auth.models import User
from yapjoy_registration.models import optionsSearch, UserProfile

class Shortlist(models.Model):
    user = models.ForeignKey(User)
    vendor = models.ForeignKey(UserProfile, null=True)

    category = models.CharField(max_length=500, blank=True, null=True)

    ACTIVE = "Active"
    PENDING = "Pending"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (PENDING, "Pending"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default=ACTIVE)

    #
    # title = models.CharField(max_length=255)
    # description = models.TextField()
    #
    # city = models.CharField(max_length=255)
    # state = models.CharField(max_length=255)
    # yelp_rate = models.IntegerField(default=4)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor.user.username
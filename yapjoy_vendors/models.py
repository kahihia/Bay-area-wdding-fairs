from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from yapjoy_market.models import Product

def get_upload_dish_image_url_s3_file_name(instance, filename):
    now = datetime.now()

    file_name = str(filename.split('.')[-2]) + '_'+ str(now.year) + '_'+ str(now.month) + '_'+ str(now.second) + '.' + str(filename.split('.')[-1])

    return "media/%s" % (file_name)


# Create your models here.
class VendorMessage(models.Model):
    sender = models.ForeignKey(User, related_name='message_sender_vendor')
    receiver = models.ForeignKey(User, related_name='message_receiver_vendor')
    product = models.ForeignKey(Product, related_name='product_vendor')

    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=1500)

    sender_view = models.BooleanField(default=True)
    receiver_view = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

from yapjoy_registration.models import optionsSearch
class VendorRegistration(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=512, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=512, null=True, blank=True)
    last_name = models.CharField(max_length=512, null=True, blank=True)
    company_name = models.CharField(max_length=512, null=True, blank=True)
    phone = models.CharField(max_length=512, null=True, blank=True)
    website_url = models.URLField(max_length=512, null=True, blank=True)
    business_location = models.CharField(max_length=512, null=True, blank=True)
    state = models.CharField(max_length=512, null=True, blank=True)
    zip = models.CharField(max_length=512, null=True, blank=True)
    code = models.CharField(max_length=512, null=True, blank=True)
    verification_code = models.CharField(max_length=512, null=True, blank=True)
    categories = models.ForeignKey(optionsSearch, null=True, blank=True)
    PENDING = "Pending"
    VERIFIED = "Verified"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
    )
    status = models.CharField(max_length=50, null=True, blank=True, choices=STATUS_CHOICES, default=PENDING)
    profession = models.CharField(max_length=512, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Package(models.Model):
    user = models.ForeignKey(User)

    price = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class VendorAlbum(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            return self.title
        return "N/A"

class VendorImage(models.Model):
    album = models.ForeignKey(VendorAlbum)
    image = models.ImageField(upload_to=get_upload_dish_image_url_s3_file_name, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
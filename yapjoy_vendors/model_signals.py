from .models import *
from django.db.models.signals import post_save
from django.utils import timezone
from yapjoy_registration.commons import id_generator

# def VendorRegistrationNotify(sender, instance, created, **kwargs):
#     if created:
# post_save.connect(VendorRegistrationNotify, sender=VendorRegistration)
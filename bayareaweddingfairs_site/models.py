from django.db import models
from yapjoy_files.models import Event_fairs
# Create your models here.


class EventFairsDetails(models.Model):
    """ Event Fairs Details """
    eventFair = models.ForeignKey(Event_fairs, null=True, blank=True)
    eventUpdate = models.CharField(help_text="Event Update", max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.eventUpdate


class ShopVendor(models.Model):
    """ Shop Vendor Categories """
    shopVendorName = models.CharField(help_text="Vendor Category Name", max_length=255, null=True, blank=True)
    shopVendorImage = models.FileField(upload_to="static/shopVendor/")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shopVendorName


class ShopVendorsItem(models.Model):
    """ Shop Vendor Items  """
    shopVendors = models.ForeignKey(ShopVendor, related_name="shopVendorsItems", null=True, blank=True)
    itemName = models.CharField(help_text="Shop Vendors Item Name", max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.itemName


class ShopVendorsItemDetail(models.Model):
    """ Vendors Items Details """
    vendorItems = models.ForeignKey(ShopVendorsItem, related_name="itemsDetails", null=True, blank=True)
    title = models.CharField(help_text="Shop Vendor Item Details", max_length=255, null=True, blank=True)
    itemDetailImage = models.FileField(upload_to="static/itemdetails/")
    website = models.CharField(max_length=1000,null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(max_length=1000)
    subject = models.CharField(max_length=1000)
    message = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Subscriptions(models.Model):
    email = models.CharField(max_length=1000)
    type = models.CharField(max_length=1000)
    is_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
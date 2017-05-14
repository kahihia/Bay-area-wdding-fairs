from django.contrib import admin
from .models import *
# Register your models here.


class EventFairsDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'eventFair', 'eventUpdate', 'created_at']
    search_fields = ['eventFair', 'eventUpdate']

admin.site.register(EventFairsDetails, EventFairsDetailsAdmin)


class ShopVendorAdmin(admin.ModelAdmin):
    list_display = ['id', 'shopVendorName', 'created_at']
    search_fields = ['shopVendorName']

admin.site.register(ShopVendor, ShopVendorAdmin)


class ShopVendorsItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'shopVendors', 'itemName', 'created_at']
    search_fields = ['shopVendors', 'itemName']

admin.site.register(ShopVendorsItem, ShopVendorsItemAdmin)


class ShopVendorsItemDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendorItems', 'title','website', 'created_at']
    search_fields = ['vendorItems', 'title']

admin.site.register(ShopVendorsItemDetail, ShopVendorsItemDetailAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    search_fields = ['email', 'name']

admin.site.register(Contact, ContactAdmin)

class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['email', 'type', 'is_subscribed', 'created_at']
    search_fields = ['email', 'type']

admin.site.register(Subscriptions, SubscriptionsAdmin)

class Record404PathModelAdmin(admin.ModelAdmin):
    list_display = ['path', 'is_fixed', 'created_at']
    search_fields = ['path']

admin.site.register(Record404PathModel, Record404PathModelAdmin)




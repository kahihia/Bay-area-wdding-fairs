from django.contrib import admin

from .models import *


class VendorMessageAdmin(admin.ModelAdmin):
    search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    list_display = ['sender','receiver', 'product','message','created_at']
admin.site.register(VendorMessage, VendorMessageAdmin)
class VendorRegistrationAdmin(admin.ModelAdmin):
    search_fields = ['user__email','user__username','email','code','verification_code']
    list_display = ['user','email','code','verification_code','created_at']
    raw_id_fields = ['user','categories']
admin.site.register(VendorRegistration, VendorRegistrationAdmin)
class VendorAlbumAdmin(admin.ModelAdmin):
    search_fields = ['user__email','user__username','title',]
    list_display = ['user','title','created_at']
    raw_id_fields = ['user']
admin.site.register(VendorAlbum, VendorAlbumAdmin)
class VendorImageAdmin(admin.ModelAdmin):
    # search_fields = ['album__user__email','album__user__username','title',]
    list_display = ['album','image','created_at']
    raw_id_fields = ['album']
admin.site.register(VendorImage, VendorImageAdmin)


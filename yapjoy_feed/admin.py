from django.contrib import admin

from .models import *
class PostAdmin(admin.ModelAdmin):
    list_display = ['user','user_wall','text','image','created_at']
admin.site.register(Post, PostAdmin)
class pictureWallAdmin(admin.ModelAdmin):
    list_display = ['user','created_at']
admin.site.register(pictureWall, pictureWallAdmin)

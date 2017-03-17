from django.contrib import admin
from .models import *
# Register your models here.
class ShortlistAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email']
    list_display = ['user','id','vendor','category', 'created_at']
admin.site.register(Shortlist, ShortlistAdmin)

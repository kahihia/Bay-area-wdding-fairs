from django.contrib import admin
from .models import *

class CSV_EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'location','date','created_at']
    search_fields = ['title', 'location','date']
admin.site.register(CSV_Event, CSV_EventAdmin)
class CSV_UserEventsAdmin(admin.ModelAdmin):
    list_display = ['event', 'user','csv_file','status','created_at']
    search_fields = ['event', 'user__username','user__email']
admin.site.register(CSV_UserEvents, CSV_UserEventsAdmin)
class CSV_UserEventListAdmin(admin.ModelAdmin):
    list_display = ['event', 'user_id','first_name','last_name','phone','city','created_at']
    search_fields = ['event', 'user_id','first_name','last_name','phone','city']
admin.site.register(CSV_UserEventList, CSV_UserEventListAdmin)
from django.contrib import admin
from .models import *


# class EventsAdmin(admin.ModelAdmin):
#    #search_fields = ['user__email', 'user__username']
#    list_display = ['user',
#                    'subject',
#                    'start_time',
#                    'end_time',
#                    'include_friends',
#                    'include_groups',
#                    'all_day'
#                    ]
# admin.site.register(Event, EventsAdmin)
# admin.site.register(Event)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['user','title','end','is_wedding','created_at']
admin.site.register(CalendarEvent, CalendarEventAdmin)
class CalendarEventUserAdmin(admin.ModelAdmin):
    list_display = ['user','calendar_event','created_at']
admin.site.register(CalendarEventUser, CalendarEventUserAdmin)
class HostEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','subject','location']
admin.site.register(HostEvent, HostEventAdmin)
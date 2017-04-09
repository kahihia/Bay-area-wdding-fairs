from django.contrib import admin
from .models import *
# Register your models here.
class EventTicketsAdmin(admin.ModelAdmin):
    list_display = ['event','email','quantity','code','is_attended','created_at']
    raw_id_fields = ['event']
admin.site.register(EventTickets, EventTicketsAdmin)
admin.site.register(Promocode)

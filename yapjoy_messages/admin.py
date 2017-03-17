from django.contrib import admin

from .models import *


class MessageAdmin(admin.ModelAdmin):
    search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    list_display = ['sender','receiver','subject','message','created_at']
admin.site.register(Message, MessageAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    search_fields = ['user__email','user__username']
    list_display = ['user','subject','message']
admin.site.register(Feedback, FeedbackAdmin)


admin.site.register(ChatConnection)
admin.site.register(NotificationConnection)

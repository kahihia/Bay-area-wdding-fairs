from django.contrib import admin
from .models import *
class EventTeamAdmin(admin.ModelAdmin):
    # search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    raw_id_fields = ['user']
    list_display = ['user','created_at']
admin.site.register(EventTeam, EventTeamAdmin)
class FriendsChatListAdmin(admin.ModelAdmin):
    # search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    raw_id_fields = ['user', 'friend']
    list_display = ['team','channel_id','event','user','friend','created_at']
admin.site.register(FriendsChatList, FriendsChatListAdmin)
class ChannelChatListAdmin(admin.ModelAdmin):
    # search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    raw_id_fields = ['user', 'friend']
    list_display = ['name','team', 'channel_id', 'event', 'user', 'created_at']
admin.site.register(ChannelChatList, ChannelChatListAdmin)
class MessagesAdmin(admin.ModelAdmin):
    # search_fields = ['sender__email','sender__username','receiver__username','receiver__email']
    raw_id_fields = ['friends_chat_list', 'channel_chat_list','team','sender']
    list_display = ['team','friends_chat_list', 'channel_chat_list', 'message', 'sender', 'created_at']
admin.site.register(Messages, MessagesAdmin)
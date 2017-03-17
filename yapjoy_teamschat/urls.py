from django.conf.urls import patterns, url, include
from .views import send_message, send_message_ios, EventSerializerView, ChannelList
from .views import *
urlpatterns = patterns('',
            url(r'^rest-auth/', include('rest_auth.urls')),
            url(r'^events/list/$', EventSerializerView.as_view(), name="teamschat_event"),
            url(r'^(?i)auth/$',  'yapjoy_teamschat.views.authView', name='teamschat_auth'),
            url(r'^(?i)chat/$',  'yapjoy_teamschat.views.chatroom', name='chatroom'),
            url(r'^(?i)eventmanager/$',  'yapjoy_teamschat.views.eventmanager', name='eventmanager'),
            url(r'^(?i)list/chat/(?P<id>.+)/$',  'yapjoy_teamschat.views.chat_list', name='chat_list'),
            url(r'^(?i)send/message/$',  send_message.as_view(), name='send_message'),
            url(r'^(?i)send/messageios/$',  send_message_ios, name='send_message_ios'),
                       #event CRUD Operation
            url(r'(?i)event/create/$', EventCreate.as_view(), name='eventcreate_ios'),
            url(r'(?i)event/delete/(?P<pk>[0-9]+)/$', EventDelete.as_view(), name='eventdelete_ios'),
            url(r'(?i)event/list/$', EventList.as_view(), name='eventlist_ios'),
            url(r'(?i)event/edit/(?P<pk>[0-9]+)/$', EventEdit.as_view(), name='eventedit_ios'),
                       #friends list CRUD operations
            url(r'(?i)friend/contribute/(?P<user_friend_id>[0-9]+)/(?P<team_id>[0-9]+)/$', FriendsCreateView.as_view(), name='FriendsCreateView_ios'),
            url(r'(?i)channel/contribute/(?P<user_friend_id>[0-9]+)/(?P<channel_id>[0-9]+)/$', ChannelCreateView.as_view(), name='ChannelCreateView_ios'),
                       #channel CRUD operations
            url(r'(?i)channel/create/(?P<event>[0-9]+)/$', ChannelCreateViewAPI.as_view(), name='channelcreate_ios'),
            url(r'(?i)channel/list/(?P<id>[0-9]+)/$', ChannelList.as_view(), name='channellist_ios'),
            url(r'(?i)channel/delete/(?P<id>[0-9]+)/$', ChannelDelete.as_view(), name='channeldelete_ios'),
            url(r'(?i)channel/edit/(?P<id>[0-9]+)/$', ChannelEdit.as_view(), name='channeledit_ios'),

            url(r'(?i)messages/history/(?P<code>.+)/$', messageHistory.as_view(), name='messageHistory_ios'),

            url(r'(?i)friend/list/(?P<id>[0-9]+)/$', FriendList.as_view(), name='channellist_ios'),
            url(r'(?i)channel/(?P<id>[0-9]+)/friends/$', ChannelFriendsList.as_view(), name='channellist_ios'),
            url(r'(?i)loginIOS/$', loginIOS.as_view(), name='loginIOS'),
       )

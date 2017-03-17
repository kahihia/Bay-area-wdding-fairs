from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    # Examples:
    url(r'^(?i)messages/$', 'yapjoy_messages.views.messages', name='messages'),
    url(r'^(?i)messagesV2/$', 'yapjoy_messages.views.messagesV2', name='messagesV2'),
    url(r'^(?i)messages/compose/$', 'yapjoy_messages.views.messages_compose', name='messages_compose'),
    url(r'^(?i)messages/composeV2/$', 'yapjoy_messages.views.messages_composeV2', name='messages_composeV2'),
    url(r'^(?i)messages/sent/$', 'yapjoy_messages.views.messages_sent', name='messages_sent'),
    url(r'^(?i)messages/sentV2/$', 'yapjoy_messages.views.messages_sentV2', name='messages_sentV2'),
    url(r'^(?i)messages/draft/$', 'yapjoy_messages.views.messages_draft', name='messages_draft'),
    url(r'^(?i)messages/draftV2/$', 'yapjoy_messages.views.messages_draftV2', name='messages_draftV2'),
    url(r'^(?i)messages/draft/(?P<id>[^\.]+)/$', 'yapjoy_messages.views.messages_draft_edit', name='messages_draft_edit'),
    url(r'^(?i)messages/draftV2/(?P<id>[^\.]+)/$', 'yapjoy_messages.views.messages_draft_editV2', name='messages_draft_editV2'),
    url(r'^(?i)messages/(?P<id>[^\.]+)/$', 'yapjoy_messages.views.messages_view', name='messages_view'),

    url(r'^(?i)online_message/$', 'yapjoy_messages.views.online_message', name='online_message'),

    url(r'^video_chat/$', 'yapjoy_messages.chat_views.video_chat', name='video_chat'),

    url(r'^get_vchat_session/$', 'yapjoy_messages.chat_views.get_vchat_session', name='get_vchat_session'),

    url(r'^text_chat/$', 'yapjoy_messages.chat_views.text_chat', name='text_chat'),

    url(r'^get_tchat_session/$', 'yapjoy_messages.chat_views.get_tchat_session', name='get_tchat_session'),

    url(r'^get_tchat_archive/$', 'yapjoy_messages.chat_views.get_tchat_archive', name='get_tchat_archive'),

    url(r'^put_tchat_data/$', 'yapjoy_messages.chat_views.put_tchat_data', name='put_tchat_data'),

    url(r'^get_notification_session/$', 'yapjoy_messages.chat_views.get_notification_session',
        name='get_notification_session'),

    url(r'^get_message_count/$', 'yapjoy_messages.chat_views.get_message_count',
        name='get_message_count'),

    url(r'^register_video_call/$', 'yapjoy_messages.chat_views.register_video_call',
        name='register_video_call'),

    url(r'^update_last_seen/$', 'yapjoy_messages.chat_views.update_last_seen', name='update_last_seen'),

    url(r'^is_online/$', 'yapjoy_messages.chat_views.is_online', name='is_online'),

    url(r'^get_chat_user_list/$', 'yapjoy_messages.chat_views.get_chat_user_list', name='get_chat_user_list'),

    url(r'^get_messages/$', 'yapjoy_messages.chat_views.get_messages', name='get_messages'),

    url(r'^get_user_picture_url/$', 'yapjoy_messages.chat_views.get_user_picture_url', name='get_user_picture_url'),
)

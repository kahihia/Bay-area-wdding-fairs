from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'yapjoy_forum.views.index', name='forum-index'),
    url(r'^(\d+)/$', 'yapjoy_forum.views.forum', name='forum-detail'),
    url(r'^topic/(\d+)/$', 'yapjoy_forum.views.topic', name='topic-detail'),
    url(r'^reply/(\d+)/$', 'yapjoy_forum.views.post_reply', name='reply'),
    url(r'newtopic/(\d+)/$', 'yapjoy_forum.views.new_topic', name='new-topic'),
    url(r'^search/$', 'yapjoy_forum.views.search', name='search'),
)

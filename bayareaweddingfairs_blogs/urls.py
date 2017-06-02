from django.conf.urls import url
from bayareaweddingfairs_blogs.views import blogs as view

urlpatterns = [

    url(r'^$', view.post_list, name='post_list'),
    url(r'^post/(?P<pk>\d+)/$', view.post_detail, name='post_detail'),
    url(r'^post/new/$', view.post_new, name='post_new'),
    url(r'^post/(?P<pk>\d+)/edit/$', view.post_edit, name='post_edit'),
    url(r'^userpost/$', view.user_post, name='user_post'),
    url(r'^postdelete/(?P<pk>\d+)/$', view.post_delete, name='post_delete'),
    url(r'^post/(?P<pk>\d+)/comment/$', view.add_comment, name='add_comment'),

]
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^$', 'yapjoy_video.views.video'),

)

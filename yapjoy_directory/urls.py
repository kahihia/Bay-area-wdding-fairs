from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^directory/$', 'yapjoy_directory.views.directory'),

)

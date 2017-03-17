from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^$', 'yapjoy_csv.views.view_csv'),
)

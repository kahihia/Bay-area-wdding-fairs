from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^events/$', 'yapjoy_events.views.events'),
        url(r'^events/edit/(?P<id>[^\.]+)/$', 'yapjoy_events.views.events_edit'),
        url(r'^events/all_events/', 'yapjoy_events.views.all_events', name='all_events'),
        url(r'^delete_events/(?P<id>[^\.]+)$', 'yapjoy_events.views.delete_events'),

        # url(r'^add_events/$', 'yapjoy_events.views.add_events'),
        # url(r'^edit_events/(?P<id>[^\.]+)$', 'yapjoy_events.views.edit_events'),
        # url(r'^(?P<id>[^\.]+)/$', 'yapjoy_events.views.view_events'),
)

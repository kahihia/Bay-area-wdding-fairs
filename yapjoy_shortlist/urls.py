from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^(?P<category>[^\.]+)/(?P<product_id>[^\.]+)/$', 'yapjoy_shortlist.views.shortlist'),
        url(r'^req/(?P<category>[^\.]+)/(?P<product_id>[^\.]+)/$', 'yapjoy_shortlist.views.shortlist_req'),
        # url(r'^addvendor/$', 'yapjoy_shortlist.views.addvendor'),
        # url(r'^deletevendor/$', 'yapjoy_shortlist.views.deletevendor'),
)
from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
                       url(r'^main/$', 'bayareaweddingfairs_tickets.views.Main'),
                       url(r'^buy/(?P<id>.+)/$', 'bayareaweddingfairs_tickets.views.BuyTickets'),
                       url(r'^promocode/', 'bayareaweddingfairs_tickets.views.PromoCode_Validate', name='promocode'),
                       url(r'^checkajax/', 'bayareaweddingfairs_tickets.views.checkout_ajax', name='checkout_ajax'),
                       # url(r'^shortlist/(?P<option_search_id>[^\.]+)/$', 'yapjoy_vendors.views.productlist'),
                       # url(r'^shortlist_req/(?P<option_search_id>[^\.]+)/$', 'yapjoy_vendors.views.productlist_req'),
                       # url(r'^message/(?P<product_id>[^\.]+)/(?P<receiver_id>[^\.]+)/$', 'yapjoy_vendors.views.vendor_message'),
                       )

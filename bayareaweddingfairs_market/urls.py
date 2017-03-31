from django.conf.urls import patterns, include, url
from bayareaweddingfairs_market.views import *

urlpatterns = patterns('',
    url(r'^$', IndexMarket, name='market_index'),
    url(r'^subscribe/$', donateMarket, name='donate_market'),
)
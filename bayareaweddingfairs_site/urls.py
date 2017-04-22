from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^shop-vendors/', ShopVendors, name="index__shop_vendors"),
    url(r'^our-events/', OurShows, name="index__our_events"),
    url(r'^$', Index),
)


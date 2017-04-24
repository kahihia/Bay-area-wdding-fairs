from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^shop-vendors/', ShopVendors, name="index__shop_vendors"),
    url(r'^our-events/', OurShows, name="index__our_events"),
    url(r'^bride-groom-registration/', BrideGroomRegistration, name="index__bride_groom_registration"),
    url(r'^become-an-exhibitor/', VendorRegistration, name="index__vendor_registration"),
    url(r'^$', Index),
   url(r'^(?P<id>[-_@.+0-9a-zA-Z ]+)/$', shopDetail, name="storefrontItemDetail")
)


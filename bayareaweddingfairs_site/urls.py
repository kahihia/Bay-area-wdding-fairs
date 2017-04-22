from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^shop_vendors/', ShopVendors),
    url(r'^$', Index),
)


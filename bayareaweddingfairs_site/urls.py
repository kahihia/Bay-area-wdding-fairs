from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
                       url(r'^shop-vendors/', ShopVendors, name="index__shop_vendors"),
                       url(r'^our-events/', OurShows, name="index__our_events"),
                       url(r'^bride-groom-registration/', BrideGroomRegistration, name="index__bride_groom_registration"),
                       # url(r'^become-an-exhibitor/', VendorRegistrationIndex, name="index__vendor_registration_index"),
                       url(r'^vendor-registration/', VendorRegistration, name="index__vendor_registration"),
                       url(r'^bride-groom-ticket/', BrideGroomTicket, name="index__bride_groom_ticket"),
                       # url(r'^bride-groom-ticket-success/', BrideGroomTicketSuccess, name="index__bride_groom_ticket_success"),
                       # url(r'^shop-vendors-details/(?P<id>\d+)/$', shopDetail, name="storefrontItemDetail"),
                       url(r'^become-an-exhibitor/', BecomeExhibitor, name="index__BecomeExhibitor"),
                       url(r'^registration-success/', VendorRegistrationThankYou, name="index__vendor_registration__success"),
                       url(r'^bride-registration-success/', BrideRegistrationThankYou, name="index__bride_registration__success"),
                       url(r'^las-vagas-signin/', LasVegasSignin, name="index__LasVegasSignin"),
                       url(r'^shop-vendors-details/(?P<id>[-_@.+0-9a-zA-Z ]+)/$', shopDetail, name="index__storefrontItemDetail"),
                     url(r'^$', Index),
                       )


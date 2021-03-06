from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from .views import *

urlpatterns = patterns('',
                       url(r'^shop-vendors/', ShopVendors, name="index__shop_vendors"),
                       url(r'^contact/', ContactView, name="index__contact"),
                       url(r'^our-events/', OurShows, name="index__our_events"),
                       url(r'^save_404_path/', Save404Path, name="index__save_404_path"),
                       url(r'^bride-groom-registration/', BrideGroomRegistration, name="index__bride_groom_registration"),
                       # url(r'^become-an-exhibitor/', VendorRegistrationIndex, name="index__vendor_registration_index"),
                       url(r'^vendor-registration/', VendorRegistration, name="index__vendor_registration"),
                       url(r'^bride-groom-ticket/', BrideGroomTicket, name="index__bride_groom_ticket"),
                       # url(r'^bride-groom-ticket-success/', BrideGroomTicketSuccess, name="index__bride_groom_ticket_success"),
                       # url(r'^shop-vendors-details/(?P<id>\d+)/$', shopDetail, name="storefrontItemDetail"),
                       url(r'^privacy-policy/', TemplateView.as_view(template_name="bayareaweddingfairs/site/PrivacyPolicy/Policy.html"), name="index__PrivacyPolicy"),
                       url(r'^become-an-exhibitor/', BecomeExhibitor, name="index__BecomeExhibitor"),
                       url(r'^registration-success/', VendorRegistrationThankYou, name="index__vendor_registration__success"),
                       url(r'^bride-registration-success/', BrideRegistrationThankYou, name="index__bride_registration__success"),
                       url(r'^las-vagas-signin/', LasVegasSignin, name="index__LasVegasSignin"),
                       url(r'^shop-vendors-details/(?P<id>[-_@.+0-9a-zA-Z ]+)/$', shopDetail, name="index__storefrontItemDetail"),
                       url(r'^$', Index),
                       url(r'event-detail/(?P<id>\d+)/', eventDetail, name="eventfair_detail" )
                       )


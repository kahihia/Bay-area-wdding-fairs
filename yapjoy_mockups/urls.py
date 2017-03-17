from django.conf.urls import patterns, include, url
from django.contrib import admin
from yapjoy import settings
from django.views.generic import RedirectView, TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    # url(r'^$',  'yapjoy_registration.views.redirect_view_select'),
    # url(r'^storefrontv2/$', 'yapjoy_vendors.views.storefrontv2', name='vendor_storefrontv2'),
   # url(r'^storefrontv2/$', TemplateView.as_view(template_name='vendroid/demov2/vendors/profile/vendor_profileFormv2.html')),
   #url(r'^splashpagenew/$', TemplateView.as_view(template_name='moments/yapjoy_splash_landing.html')),
   #url(r'^storefrontbuildernew/$', TemplateView.as_view(template_name='vendroid/demov2/vendors/profile/yapjoy_storefront/storefront_builder.html')),
   # url(r'^eventdetailnew/$', TemplateView.as_view(template_name='vendroid/demov2/vendors/profile/yapjoy_event/yapjoy_event_detail.html')),
   # url(r'^ypmyeventsnew/$', TemplateView.as_view(template_name='vendroid/demov2/vendors/profile/yapjoy_event/yapjoy_my_events.html')),
   # url(r'^ypbridegroomsplash/$', TemplateView.as_view(template_name='vendroid/demov2/bride_groom_splah/bride_groom_splah_login.html')),
   url(r'^ypchat/$', TemplateView.as_view(template_name='vendroid/demov2/vendors/teamChat/yapjoy_chat/chat.html')),
)

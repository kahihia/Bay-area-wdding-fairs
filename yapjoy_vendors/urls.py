from django.conf.urls import patterns, include, url

from rest_framework.urlpatterns import format_suffix_patterns
from .vendorApi import *

urlpatterns = patterns('',
                       url(r'^dashboard/(?P<option_id>[^\.]+)/$', 'yapjoy_vendors.views.dashboard', name='yapjoy_vendors_dashboard'),
                       url(r'^shortlist/(?P<option_search_id>[^\.]+)/$', 'yapjoy_vendors.views.productlist'),
                       url(r'^shortlist_req/(?P<product_id>[^\.]+)/$', 'yapjoy_vendors.views.productlist_req'),
                       url(r'^message/(?P<product_id>[^\.]+)/(?P<receiver_id>[^\.]+)/$', 'yapjoy_vendors.views.vendor_message'),
                       url(r'^answer/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/(?P<user_id>[^\.]+)/$', 'yapjoy_vendors.views.answer'),
                       url(r'^dreams/(?P<id>[^\.]+)/(?P<user_id>[^\.]+)/$', 'yapjoy_vendors.views.dream_req'),
                       url(r'^(?i)select/$', 'yapjoy_vendors.views.SelectStep', name='yapjoy_vendor_select'),
                       url(r'^listing/$', 'yapjoy_vendors.views.ListingView', name='vendors__storelisting'),
                       url(r'^listing/subscription/(?P<id>[^\.]+)/$', 'yapjoy_vendors.views.Subscription', name='vendors__subscription'),
                       url(r'^listing/dream/(?P<id>[^\.]+)/$', 'yapjoy_vendors.views.dream_req',name='vendors__listing_dream'),
                       url(r'^listing/answer/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/(?P<user_id>[^\.]+)/$',
                                   'yapjoy_vendors.views.listing_answer', name="vendors__listing_answer"),
                        url(r'^listing/bid/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/(?P<user_id>[^\.]+)/$',
                                   'yapjoy_vendors.views.listing_bid', name="vendors__listing_bid"),
                       #url(r'^storefront/$', 'yapjoy_vendors.views.StoreFrontView', name='vendors__storefront'),
                       url(r'^storefront/editor/$', 'yapjoy_vendors.views.StoreFrontEdit', name='vendors__storefrontEdit'),
                       url(r'^verify/(?P<code>[^\.]+)/$', 'yapjoy_vendors.views.verify_email', name='vendors__verify__code'),
                       url(r'^setup/(?P<code>[^\.]+)/$', 'yapjoy_vendors.views.SetupPasswordView', name='vendors__setup_password'),
                       url(r'^profile/$', 'yapjoy_vendors.views.profile', name='vendors__profile'),
                       url(r'^profile/view/(?P<id>[^\.]+)/$', 'yapjoy_vendors.views.profileView', name='vendors__profile_view'),
                       url(r'^profile/admin/view/(?P<profile_id>[^\.]+)/$', 'yapjoy_vendors.views.profile_admin_view', name='vendors__profile__admin__view'),
                       url(r'^profile/admin/$', 'yapjoy_vendors.views.profile_admin', name='vendors__profiles__admin'),


                       ### Vendor Registration API

                       url(r'^api/vendorlogin/$', LoginUser.as_view(), name="vendors__loginapi"),
                       url(r'^api/vendorregister/$', VendorRegister.as_view(), name="vendors__regsiterapi"),
                       url(r'^api/verification/(?P<token>[a-zA-Z0-9_]+)/(?P<email>[-_@.+0-9a-zA-Z ]+)/$', EmailVerification.as_view(), name="vendors__verification"),
                       url(r'^api/setpassword/(?P<token>[a-zA-Z0-9_]+)/(?P<email>[-_@.+0-9a-zA-Z ]+)/$', SetPassword.as_view(), name="vendors__setpassword"),
                       url(r'^api/logout/', LogoutUser.as_view(), name='vendors_logoutapi'),

                        #IOS API URLS
                       url(r'^api/vendorregisterIOS/$', VendorRegisterIOS.as_view(), name="vendors__regsiterapiIOS"),
                       url(r'^api/verificationIOS/(?P<token>[a-zA-Z0-9_]+)/(?P<email>[-_@.+0-9a-zA-Z ]+)/$', EmailVerificationIOS.as_view(), name="vendors__verificationIOS"),
                       url(r'^api/setpasswordIOS/(?P<token>[a-zA-Z0-9_]+)/(?P<email>[-_@.+0-9a-zA-Z ]+)/$', SetPasswordIOS.as_view(), name="vendors__setpasswordIOS"),

                       ## URLS
                       # url(r'^storefront/$', 'yapjoy_vendors.views.StoreFrontv2', name='vendors__storefront'),
                       url(r'^sign_s3/$', 'yapjoy_vendors.views.sign_s3', name='vendors__sign_s3'),
                       url(r'^storefront/$', VendorRegister.as_view(), name='vendors__storefront'),
                       url(r'^invitation/$', 'yapjoy_vendors.views.invitation', name='vendors__invitationm'),
                      # url(r'^invitation/$', 'yapjoy_vendors.views.invitation', name='vendors__invitation'),
                       url(r'^bg/page/$', 'yapjoy_vendors.views.bg_page', name='page'),
                       )

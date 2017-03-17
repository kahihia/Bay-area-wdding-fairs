from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from yapjoy import settings
from django.views.generic import RedirectView, TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^crm/', include('yapjoy_files.urls')),
    url(r'^$',  'yapjoy_registration.views.redirect_view_select'),

    url(r'^', include('yapjoy_events.urls')),
    url(r'^tasks/', include('yapjoy_tasks.urls')),
    url(r'^', include('yapjoy_directory.urls')),
    # url(r'^(?i)notificationsV2/$', 'yapjoy_registration.views.notificationsV2', name='notificationsV2'),
    url(r'^', include('yapjoy_messages.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^shortlist/', include('yapjoy_shortlist.urls')),
    url(r'^', include('yapjoy_market.urls')),
    url(r'^s3direct/', include('yapjoy_s3direct.urls')),
    url(r'^forum/', include('yapjoy_forum.urls')),



    url(r'^(?i)activate/(?P<code>[\w:-]+)', 'yapjoy_registration.views.activate', name='activate'),
    url(r'^(?i)send_email/$', 'yapjoy_registration.views.send_email', name='send_email'),
    url(r'^(?i)invitation/accept/(?P<email>[-_@.+0-9a-zA-Z ]+)/', 'yapjoy_registration.views.invite_accept', name='invite_accept'),
    # url(r'^(?i)login_old/', 'yapjoy_registration.views.login', name='login'),
    url(r'^(?i)login/', 'yapjoy_registration.views.admin_login'),
    url(r'^(?i)crm/login/', 'yapjoy_registration.views.admin_login', name='admin_login'),
    url(r'^(?i)register/', 'yapjoy_registration.views.register', name='register'),
    url(r'^(?i)registration/wizard/(?P<code>[^\.]+)/', 'yapjoy_registration.views.registeration_wizard', name='registeration_wizard'),
    url(r'^(?i)subscribe/$', 'yapjoy_registration.views.subscribe', name='subscribe'),
    url(r'^(?i)invoices/$', 'yapjoy_registration.views.invoices', name='invoices_view_main'),
    # url(r'^(?i)invoices/bulk/$', 'yapjoy_registration.views.invoices_bulk', name='invoices_bulk_view_main'),
    url(r'^(?i)invoices/pay/(?P<code>.+)/$', 'yapjoy_registration.views.invoices_pay', name='invoices_view_pay'),
    url(r'^(?i)invoices/card/change/(?P<code>.+)$', 'yapjoy_registration.views.card_change_view', name='card_change_view'),
    url(r'^(?i)invoices/deposit/pay/(?P<code>.+)/(?P<code2>.+)$', 'yapjoy_registration.views.invoices_deposit_pay_main', name='invoices_deposit_pay_main'),
    url(r'^(?i)invoices/deposit/view/(?P<code>.+)/(?P<code2>.+)$', 'yapjoy_registration.views.invoices_deposit_view_main', name='invoices_deposit_view_main'),
    url(r'^(?i)invoices/bulk/pay/(?P<id>.+)/$', 'yapjoy_registration.views.invoices_pay_bulk', name='invoices_pay_bulk'),
    url(r'^(?i)subscribtion_wizard/(?P<code>[\w:-]+)/', 'yapjoy_registration.views.subscribtionCode', name='subscribe'),
    # url(r'^(?i)landing/', 'yapjoy_registration.views.landing', name='landing'),
    # url(r'^(?i)loginV2/', 'yapjoy_registration.views.loginV2'),
    url(r'^(?i)forgotPassword/', 'yapjoy_registration.views.forgotPassword', name='forgotPassword'),
    url(r'^(?i)forgotPasswordV2/', 'yapjoy_registration.views.forgotPasswordV2', name='forgotPasswordV2'),
    url(r'^(?i)reset_password/(?P<code>[^\.]+)/', 'yapjoy_registration.views.ResetPassword', name='resetPassword'),
    url(r'^(?i)reset_passwordV2/(?P<code>[^\.]+)/', 'yapjoy_registration.views.ResetPasswordV2', name='resetPasswordV2'),
    # url(r'^(?i)logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}),
    url(r'^(?i)logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^api_friends/$', 'yapjoy_registration.views.api_friends', name='api_friends'),
    url(r'^privacy_policy/$', 'yapjoy_registration.views.privacy_policy', name='api_friends'),
    url(r'^terms_and_conditions/$', 'yapjoy_registration.views.terms_and_conditions', name='api_friends'),
    # Uncomment the next line to enable the admin:
    url(r'^bayareaweddingfairs/tickets/', include('bayareaweddingfairs_tickets.urls')),
    url(r'^api/', include('yapjoy_api.urls')),
    url(r'^csv/', include('yapjoy_csv.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^invite/$', 'yapjoy_registration.views.invite_friends'),
    url(r'^invites/', include("django_contact_importer.contacts.urls")),
    url(r'^video/', include("yapjoy_video.urls")),
    #url(r'^video/', include("yapjoy_video.urls")),


)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += patterns('', (
    r'^static/(?P<path>.*)$',
    'django.views.static.serve',
    {'document_root': settings.STATIC_ROOT}
))

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     )

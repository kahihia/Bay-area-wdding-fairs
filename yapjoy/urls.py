from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from yapjoy import settings
from django.views.generic import RedirectView, TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^crm/', include('yapjoy_files.urls')),
    url(r'^pusher/', include('yapjoy_teamschat.urls')),
    url(r'^vendors/', include('yapjoy_vendors.urls')),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    # url(r'^$',  RedirectView.as_view(url='/plans/')),
    # url(r'^$',  RedirectView.as_view(url='/plans/')),
    url(r'^$',  'yapjoy_registration.views.redirect_view_select'),
    # url(r'^(?i)loginv2/$',  TemplateView.as_view(template_name="moments/home.html")),
    # url(r'^(?i)loginv2/$',  'yapjoy_registration.views.loginv2', name='loginv2'),
    url(r'^(?i)login/professional/$',  'yapjoy_registration.views.login_professional', name='login_professional'),
    # url(r'^(?i)login/$',  'yapjoy_registration.views.loginv3', name='login'),
    url(r'^(?i)login/$',  'yapjoy_registration.views.loginv3pre', name='pre_login'),

    # url(r'^(?i)dashboardV2/', 'yapjoy_registration.views.dashboardV2'),
    url(r'^(?i)choose_profile/', 'yapjoy_registration.views.choose_profile', name='choose_profile'),
    url(r'^(?i)unsubscribeuser/(?P<code>[^\.]+)/$', 'yapjoy_registration.views.unsubscribeuser', name='unsubscribeuser'),
    url(r'^(?i)friends/$', 'yapjoy_registration.views.friends', name='friends'),
    url(r'^(?i)followers/$', 'yapjoy_registration.views.followers', name='followers'),
    # url(r'^(?i)friendsV2/$', 'yapjoy_registration.views.friendsV2', name='friendsV2'),
    url(r'^(?i)friends/delete/$', 'yapjoy_registration.views.friends_delete', name='friends_delete'),
    url(r'^(?i)professionals/$', 'yapjoy_registration.views.professionals', name='professionals'),
    # url(r'^(?i)professionalsV2/$', 'yapjoy_registration.views.professionalsV2', name='professionalsV2'),
    url(r'^(?i)professional/profile/(?P<id>.+)/$', 'yapjoy_registration.views.professional_profile', name='professional_profile'),
    # url(r'^(?i)events/$', 'yapjoy_registration.views.events', name='events'),
    # url(r'^(?i)tasks/$', 'yapjoy_registration.views.tasks', name='tasks'),
    url(r'^', include('yapjoy_events.urls')),
    url(r'^tasks/', include('yapjoy_tasks.urls')),
    url(r'^', include('yapjoy_directory.urls')),
    url(r'^(?i)recommend/$', 'yapjoy_registration.views.recommend', name='recommend'),
    url(r'^(?i)seatingCharts/$', 'yapjoy_registration.views.seatingCharts', name='seatingCharts'),

    # #---------------------Demo Urls---------------------------------
    # url(r'^(?i)demo/survey/venue/(?P<id>.+)/(?P<qno>.+)/$', 'yapjoy_market.demo.QuestionVenue', name='QuestionVenue'),
    # url(r'^(?i)demo/survey/dj/(?P<id>.+)/(?P<qno>.+)/$', 'yapjoy_market.demo.QuestionDJ', name='QuestionDJ'),
    # url(r'^(?i)demo/select/(?P<id>.+)/$', 'yapjoy_market.demo.SelectStep', name='SelectStep'),
    # url(r'^(?i)demo/plans/(?P<id>.+)/(?P<type>[\w:-]+)/$', 'yapjoy_market.demo.PlansStep', name='PlansStep'),
    # url(r'^(?i)demo/result/(?P<id>.+)/(?P<type>[\w:-]+)/$', 'yapjoy_market.demo.PlansResult', name='PlansResult'),
    # url(r'^(?i)demo/$', 'yapjoy_market.demo.EmailStep', name='EmailStep'),
    # #---------------------------------------------------------------
    #---------------------Demo V2 Urls---------------------------------
    url(r'^(?i)demov2/survey/venue/(?P<id>.+)/(?P<qno>.+)/$', 'yapjoy_market.demov2.QuestionVenue', name='QuestionVenuev2'),
    url(r'^(?i)demov2/survey/dj/(?P<id>.+)/(?P<qno>.+)/$', 'yapjoy_market.demov2.QuestionDJ', name='QuestionDJv2'),
    url(r'^(?i)select/$', 'yapjoy_market.demov2.SelectStep', name='select'),
    # url(r'^(?i)demov2/select/(?P<id>.+)/$', 'yapjoy_market.demov2.SelectStepV2', name='SelectStepVer2'),
    # url(r'^(?i)demov2/plans/(?P<id>.+)/(?P<user_id>.+)/$', 'yapjoy_market.demov2.PlansStepV2', name='PlansStepver2'),
    # url(r'^(?i)plans/$', 'yapjoy_market.demov2.PlansStep', name='PlansStepv2'),
    url(r'^(?i)demov2/result/(?P<id>.+)/(?P<type>[\w:-]+)/$', 'yapjoy_market.demov2.PlansResult', name='PlansResultv2'),
    url(r'^(?i)demov2/$', 'yapjoy_market.demo.EmailStep', name='EmailStepv2'),
    #---------------------------------------------------------------

    url(r'^(?i)dashboard/$', 'yapjoy_registration.views.dashboard', name='dashboard'),
    url(r'^(?i)all_leads/$', 'yapjoy_registration.views.all_leads', name='all_leads'),
    url(r'^(?i)instagram/$', 'yapjoy_registration.views.instagram', name='instagram'),

    url(r'^(?i)dashboardTest/$', 'yapjoy_registration.views.dashboardTest', name='dashboardTest'),
    url(r'^(?i)notifications/$', 'yapjoy_registration.views.notifications', name='notifications'),
    # url(r'^(?i)notificationsV2/$', 'yapjoy_registration.views.notificationsV2', name='notificationsV2'),
    url(r'^', include('yapjoy_messages.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^shortlist/', include('yapjoy_shortlist.urls')),
    url(r'^', include('yapjoy_market.urls')),
    url(r'^(?i)feedback/$', 'yapjoy_registration.views.feedback', name='feedback'),
    url(r'^(?i)support/$', 'yapjoy_registration.views.support', name='support'),
    url(r'^(?i)recommendations/$', 'yapjoy_registration.views.recommendations', name='recommendations'),
    # url(r'^(?i)recommendationsV2/$', 'yapjoy_registration.views.recommendationsV2', name='recommendationsV2'),
    url(r'^s3direct/', include('yapjoy_s3direct.urls')),
    url(r'^forum/', include('yapjoy_forum.urls')),
    # url(r'^(?i)forumV2/', 'yapjoy_forum.views.indexV2', name='forum-indexV2'),
    # url(r'^(?i)forumdetailV2/(\d+)/$', 'yapjoy_forum.views.forumV2', name='forumdetailV2'),
    # url(r'^(?i)topicV2/(\d+)/$', 'yapjoy_forum.views.topicV2', name='topic-detailV2'),

    url(r'^(?i)bg/profile/$', 'yapjoy_registration.views.bg_profile', name='bg_profile'),
    url(r'^family_share_link/(?P<code>[a-zA-Z0-9_]+)/$', 'yapjoy_vendors.views.invitationfamily',name='family__invitation'),
    url(r'^vendor_share_link/(?P<code>[a-zA-Z0-9_]+)/$', 'yapjoy_vendors.views.invitationvendor',name='vendor__invitation'),

    url(r'^(?i)bg/event/create/$', 'yapjoy_registration.views.bg_event_create', name='bg_event_create'),
    url(r'^(?i)profile/$', 'yapjoy_registration.views.profile', name='profile'),
    url(r'^(?i)ajax_feed/(?P<index>.+)/$', 'yapjoy_registration.views.wall_feed_ajax', name='wall_feed_ajax'),
    url(r'^(?i)profile/(?P<id>.+)/$', 'yapjoy_registration.views.public_profile', name='public_profile'),
    # url(r'^(?i)settings/$', 'yapjoy_registration.views.settings_view', name='settings'),
    url(r'^(?i)settings/$', 'yapjoy_registration.views.settings_view_v2', name='settings'),
    url(r'^(?i)settings/delete/$', 'yapjoy_registration.views.settings_delete', name='settings_delete'),
    url(r'^(?i)company/settings/$', 'yapjoy_registration.views.company_settings_view', name='company_settings'),

    url(r'^(?i)subscribeiFrame/$', 'yapjoy_accounts.views.creditBuyiFrame', name='creditBuy'),
    url(r'^(?i)subscribeiFrameCoin/$', 'yapjoy_accounts.views.creditBuyiFrameCoin', name='creditBuyCoin'),
    url(r'^(?i)creditBuy/(?P<id>.+)/$', 'yapjoy_accounts.views.creditBuy', name='creditBuy'),
   # url(r'^(?i)creditBuy/(?P<id>.+)/$', 'yapjoy_accounts.views.creditBuy', name='creditBuy'),
    url(r'^(?i)credit/$', 'yapjoy_accounts.views.credit', name='credit'),
    url(r'^(?i)removeCard/$', 'yapjoy_accounts.views.removeCard'),


    url(r'^(?i)activate/(?P<code>[\w:-]+)', 'yapjoy_registration.views.activate', name='activate'),
    url(r'^(?i)send_email/$', 'yapjoy_registration.views.send_email', name='send_email'),
    url(r'^(?i)invitation/accept/(?P<email>[-_@.+0-9a-zA-Z ]+)/', 'yapjoy_registration.views.invite_accept', name='invite_accept'),
    # url(r'^(?i)login_old/', 'yapjoy_registration.views.login', name='login'),
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
    url(r'^(?i)logout/vendor/$', 'django.contrib.auth.views.logout', {'next_page': '/login/professional'}, name="logout__vendor"),
    # url(r'^yapjoy/', include('yapjoy.foo.urls')),

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
    url(r'^chat/', include("jqchat.urls")),

   url(r'^mockups/', include("yapjoy_mockups.urls")),

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

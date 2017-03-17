from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
        url(r'^plans/$', 'yapjoy_market.views.myPlanner'),
        url(r'^market/$', 'yapjoy_market.views.market'),
        url(r'^marketV2/(?P<id>[^\.]+)/$', 'yapjoy_market.views.marketV2'),
        url(r'^productbudget/completing/$', 'yapjoy_market.views.awardSubBudget'),
        url(r'^productbudget/changebudget/$', 'yapjoy_market.views.changebudget'),
        url(r'^productbudget/deletebudget/$', 'yapjoy_market.views.deletebudget'),
        # url(r'^changeTotalAmount/$', 'yapjoy_market.views.changeTotalAmount'),
        url(r'^plans/(?P<id>[^\.]+)/$', 'yapjoy_market.views.plans_detail'),
        url(r'^market/(?P<id>[^\.]+)/$', 'yapjoy_market.views.market_detail'),
        url(r'^growthgraph/plans/$', 'yapjoy_market.views.growthGraph'),
        url(r'^growthgraph/plans/$', 'yapjoy_market.views.growthGraph'),
        url(r'^rsvp/$', 'yapjoy_market.views.rsvp'),
        url(r'^invite/(?P<id>[^\.]+)/$', 'yapjoy_market.views.invite_user'),
        url(r'^invitationaccepted/(?P<userid>[^\.]+)/(?P<invitedid>[^\.]+)/(?P<code>[^\.]+)/$', 'yapjoy_market.views.acceptRsvp'),
        url(r'^acceptedinvitation/(?P<userid>[^\.]+)/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<code>[^\.]+)/$', 'yapjoy_market.views.acceptRsvpEmail'),

        url(r'^questionadmin/$', 'yapjoy_market.views.questionAdmin'),
        #Steps/Questions
        url(r'^question/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/(?P<user_id>[^\.]+)/$',
           'yapjoy_market.views.question'),
        url(r'^question_req/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/$',
           'yapjoy_market.views.question_req'),
        url(r'^question_general/$',
           'yapjoy_market.views.question_general'),
        url(r'^answer/(?P<option_search_id>[^\.]+)/(?P<product_id>[^\.]+)/(?P<user_id>[^\.]+)/$',
           'yapjoy_market.views.answer'),
        url(r'^dream/(?P<id>[^\.]+)/$', 'yapjoy_market.views.dream'),
        url(r'^dream_req/(?P<id>[^\.]+)/$', 'yapjoy_market.views.dream_req')

        # url(r'^events/edit/(?P<id>[^\.]+)/$', 'yapjoy_events.views.events_edit'),
        # url(r'^events/all_events/', 'yapjoy_events.views.all_events', name='all_events'),
        # url(r'^delete_events/(?P<id>[^\.]+)$', 'yapjoy_events.views.delete_events'),

        # url(r'^add_events/$', 'yapjoy_events.views.add_events'),
        # url(r'^edit_events/(?P<id>[^\.]+)$', 'yapjoy_events.views.edit_events'),
        # url(r'^(?P<id>[^\.]+)/$', 'yapjoy_events.views.view_events'),
)

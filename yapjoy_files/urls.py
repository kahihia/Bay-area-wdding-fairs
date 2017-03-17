from django.conf.urls import patterns, url

urlpatterns = patterns('',
       # url(r'^invoice/$', 'yapjoy_files.views.invoice', name='invoice'),
       url(r'^invoices/add/$', 'yapjoy_files.views.event_management', name='event_management'),
       url(r'^invoices/addition/iframe/$', 'yapjoy_files.views.event_management_iframe', name='event_management_iframe'),
       url(r'^local/invoices/addition/iframe/$', 'yapjoy_files.views.event_management_iframe_local', name='event_management_iframe_local'),
       url(r'^invoices/addition/success/iframe/$', 'yapjoy_files.views.event_management_iframe_success', name='event_management_iframe_success'),
       url(r'^invoices/addition/bg/success/iframe/$', 'yapjoy_files.views.event_management_iframe_bg_success', name='event_management_iframe_bg_success'),
       url(r'^invoices/addition/bg/success/iframev2/$', 'yapjoy_files.views.event_management_iframe_bg_successv2', name='event_management_iframe_bg_successv2'),

       url(r'^registration/bg/success/iframe/$', 'yapjoy_files.views.event_register_iframe_bg_success', name='event_management_iframe_bg_success'),
       url(r'^invoices/interested/$', 'yapjoy_files.views.interested_contractor', name='interested_contractor'),
       url(r'^invoices/events/$', 'yapjoy_files.views.events_based_list', name='events_based_list'),
       url(r'^invoices/eventsbg/$', 'yapjoy_files.views.events_based_list_bg', name='events_based_list_bg'),
       url(r'^invoices/commission/$', 'yapjoy_files.views.commission', name='commission'),
       url(r'^invoices/interested_detail/(?P<id>.+)/$', 'yapjoy_files.views.interested_contractor_detail', name='interested_contractor_detail'),


       url(r'^invoices/contracted/$', 'yapjoy_files.views.contracted_contractor', name='contracted_contractor'),
       url(r'^invoices/contracted_detail/(?P<id>.+)/$', 'yapjoy_files.views.contracted_contractor_detail', name='contracted_contractor_detail'),
       url(r'^invoices/bride_detail/(?P<id>.+)/$', 'yapjoy_files.views.bride_detail', name='bride_detail'),

       url(r'^bridegroom/reg/$', 'yapjoy_files.views.bg_management', name='bridegroom_reg'),
       url(r'^bridegroom/regv2/$', 'yapjoy_files.views.bg_managementv2', name='bridegroom_regv2'),
       url(r'^bridegroom/dev/reg/$', 'yapjoy_files.views.bg_management_dev', name='bg_management_dev'),
       url(r'^bridegroom/list/$', 'yapjoy_files.views.interested_bg', name='interested_bg'),
       url(r'^bridegroom/bg/list$', 'yapjoy_files.views.EventList_bg', name='events_bg'),
       url(r'^bridegroom/bg/list/csv', 'yapjoy_files.views.EventList_bg_CSV',
           name='download_events_bg'),
       url(r'^bridegroom/bg/promolist', 'yapjoy_files.views.promocodelist_bg', name='promocode_bg'),
       url(r'^bridegroom/bg/promo/populate/(?P<id>.+)', 'yapjoy_files.views.populate_Promocode_bg',
           name='edit_Promocode_bg'),
       url(r'^bridegroom/bg/promo/edit', 'yapjoy_files.views.edit_Promocode_bg',
           name='edit_Promocode_bg'),
       url(r'^LasVegasReg/$', 'yapjoy_files.views.LasVegasReg', name='LasVegasReg'),

       # new Search for bride & grooms, contracted vendors and interested vendors
       url(r'^search/', 'yapjoy_files.views.search', name='search'),
       url(r'^searchcontracted/', 'yapjoy_files.views.search_contracted', name='search_contracted'),
       url(r'^searchbridegrooms/', 'yapjoy_files.views.search_bridegrooms', name='search_bridegrooms'),
       url(r'^generatecsv/', 'yapjoy_files.views.csv_generate', name='generatecsv'),


       url(r'^invoices/create/(?P<id>.+)/$', 'yapjoy_files.views.invoice_add', name='event_management_create'),

       # url(r'^invoices/interested/$', 'yapjoy_files.views.interested_contractor', name='interested_contractor'),
       # url(r'^invoices/interested_detail/(?P<id>.+)/$', 'yapjoy_files.views.interested_contractor_detail', name='interested_contractor_detail'),
       #
       # url(r'^invoices/contracted/$', 'yapjoy_files.views.contracted_contractor', name='contracted_contractor'),
       # url(r'^invoices/contracted_detail/(?P<id>.+)/$', 'yapjoy_files.views.contracted_contractor_detail', name='contracted_contractor_detail'),


       url(r'^invoices/$', 'yapjoy_files.views.event_invoice', name='event_invoice'),
       url(r'^mediakit/$', 'yapjoy_files.views.media_kit', name='media_kit'),
       url(r'^mediakit/view/(?P<code>[^\.]+)/$', 'yapjoy_files.views.media_kit_view', name='media_kit_view'),
       url(r'^mediakit/viewv2/(?P<code>[^\.]+)/$', 'yapjoy_files.views.media_kit_viewv2', name='media_kit_view2'),
       url(r'^invoices/bulk/$', 'yapjoy_files.views.event_invoice_bulk', name='event_invoice_bulk'),
       url(r'^invoices/bulk/create/$', 'yapjoy_files.views.event_invoice_bulk_create', name='event_invoice_bulk_create'),
       url(r'^invoices/edit/(?P<id>.+)/$', 'yapjoy_files.views.event_invoice_edit_detail', name='event_invoice_edit_detail'),
       url(r'^invoices/detail/(?P<id>.+)/$', 'yapjoy_files.views.event_invoice_detail', name='event_invoice_detail'),
       url(r'^data/$', 'yapjoy_files.views.invoices_data', name='invoices_data'),
       url(r'^data/purchase/$', 'yapjoy_files.views.invoices_data_purchase', name='invoices_data_purchase'),
       url(r'^data/(?P<id>.+)/$', 'yapjoy_files.views.invoices_data_view', name='invoices_data_view'),
       url(r'^dataview/(?P<id>.+)/$', 'yapjoy_files.views.invoicesdataview_list', name='invoicesdataview_list'),
       url(r'^databuy/(?P<id>.+)/$', 'yapjoy_files.views.CSVBuyiFrameCoin', name='CSVBuyiFrameCoin'),

       url(r'^invoices/accept/bulk/(?P<code>[^\.]+)/$', 'yapjoy_files.views.event_invoice_accept_bulk', name='event_invoice_accept_bulk'),
       url(r'^invoices/accept/(?P<code>[^\.]+)/$', 'yapjoy_files.views.event_invoice_accept', name='event_invoice_accept'),
       url(r'^view/agreement/(?P<code>[^\.]+)/$', 'yapjoy_files.views.crm_view_agreement', name='crm_view_agreement'),
       url(r'^view/complete/agreement/(?P<code>[^\.]+)/$', 'yapjoy_files.views.crm_view_complete_agreement', name='crm_view_complete_agreement'),
       url(r'^invoices/bulk/pay/(?P<id>.+)/$', 'yapjoy_files.views.event_invoice_pay_bulk', name='event_invoice_pay_bulk'),
       # url(r'^invoices/pay/(?P<id>.+)/$', 'yapjoy_files.views.event_invoice_pay', name='event_invoice_pay'),
       # url(r'^invoices/deposit/pay/(?P<id>.+)/$', 'yapjoy_files.views.event_invoice_deposit_pay', name='event_invoice_deposit_pay'),
       url(r'^$', 'yapjoy_files.views.crm', name='customer_relationship_management'),
       url(r'^fileload/$', 'yapjoy_files.views.FileLoading', name='crm_file_load'),
       url(r'^event/$', 'yapjoy_files.views.CreateEvent', name='crm_create_event'),
       url(r'^createWpform/$', 'yapjoy_files.views.CreateWpForm', name='crm_create_wp_form'),
       url(r'^viewWpform/$', 'yapjoy_files.views.ViewWpForm', name='crm_view_wp_form'),
       url(r'^wizard/invoice_create/(?P<email>[-_@.+0-9a-zA-Z ]+)/', 'yapjoy_files.views.Wizard_st1', name='Wizard_st1'),

       url(r'^taskslist/$', 'yapjoy_files.views.TasksList', name='tasks_list'),

       url(r'^invoices/ticketing/', 'yapjoy_files.views.ticketingPrice', name='ticketingPrice'),
       url(r'^invoices/search', 'yapjoy_files.views.ticket_search', name='ticketsearch'),
       url(r'^eventdata', 'yapjoy_files.views.eventdata', name='eventdata'),
       )

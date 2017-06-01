from django.conf.urls import url

from django.conf.urls.static import static

from django.conf import settings

from bayareaweddingfairs_blogs.views import *



# urlpatterns = [
#
#     url(r'^$', views.post_list, name='post_list'),
#     url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
#     url(r'^post/new/$', views.post_new, name='post_new'),
#     url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
#     url(r'^drafts/$', views.post_draft_list, name='post_draft_list'),
#     url(r'^signup/$', views.signup, name='sign_up'),
#     url(r'^loginn/$', views.loginn, name='sign_in'),
#     url(r'^userpost/$', views.user_post, name='user_post'),
#     url(r'^logout/$', views.logout_view, name='log_out'),
#     url(r'^postdelete/(?P<pk>\d+)/$', views.post_delete, name='post_delete'),
#     url(r'^post/(?P<pk>\d+)/comment/$', views.add_comment, name='add_comment'),
#     url(r'^checkout/', views.checkout, name='checkout'),
#     url('^ajax/', views.render_ajax, name='render_ajax'),
#     url(r'^checkajax/', views.checkout_ajax, name='checkout_ajax'),
#     url(r'^cloudinary/', 'cloudinaryapp.views.home', name='cloudinary'),
#     url(r'^csvDatabase/', 'csv_data.views.csv_database', name='csv_data'),
#     # url(r'^scrap/', views.scrap, name='scrap'),
#
#     #url(r'^Databaseexcel/', 'csv_data.views.excel_database', name='excel_database'),
#     #url(r'^dayoff/', 'csv_data.views.dayoff_calendar', name='dayoff'),
#     #url(r'^calendar/', 'csv_data.views.calendar', name='calendar'),
#
#
#    # url(r'^css/$', blog, name='blog_static_css'),
# ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
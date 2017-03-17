from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
                       url(r'^$', 'yapjoy_tasks.views.tasks'),
                       url(r'^edit/(?P<tasks_id>[^\.]+)/$', 'yapjoy_tasks.views.edit_tasks'),
                       url(r'^complete/$', 'yapjoy_tasks.views.complete_tasks'),
                       url(r'^taskcompletechart/$', 'yapjoy_tasks.views.taskComplete'),
                       # url(r'^today/$', 'yapjoy_tasks.views.today_tasks'),
                       # url(r'^completed/$', 'yapjoy_tasks.views.completed_tasks'),
                       # url(r'^add_tasks/$', 'yapjoy_tasks.views.add_tasks'),
                       # url(r'^delete_tasks/(?P<tasks_id>\d+)/$', 'yapjoy_tasks.views.delete_tasks'),
                       # url(r'^view/(?P<tasks_id>[^\.]+)/$', 'yapjoy_tasks.views.view_tasks'),
                       )

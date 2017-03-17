from django.conf.urls import patterns, url
from yapjoy_s3direct.views import get_upload_params

urlpatterns = patterns('',
                       url('^get_upload_params/',
                           get_upload_params, name='s3direct'),
                       )

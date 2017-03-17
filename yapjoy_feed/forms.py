__author__ = 'Adeel'
from django import forms
from .models import *
from yapjoy_s3direct.widgets import S3DirectWidget
class pictureWallForm(forms.Form):
    # picture = forms.URLField(widget=S3DirectWidget(dest='imgs'))
    picture = forms.ImageField()
    # class Meta:
    #     model = pictureWall
    #     fields = ['picture',]
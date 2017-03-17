__author__ = 'Adeel'
from django import forms
from yapjoy_s3direct.widgets import S3DirectWidget

class messageForm(forms.Form):
    # subject = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Subject Title'}), required=True, error_messages={'required':'Subject is required.'})
    message = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Write your message here'}), required=True, error_messages={'required':'Message is required.'})
    images = forms.URLField(widget=S3DirectWidget(dest='imgs'), required=False)


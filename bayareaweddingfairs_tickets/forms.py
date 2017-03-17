from yapjoy.settings import *
from django.forms import ModelForm
from datetime import datetime
from django import forms
from django.core.validators import ValidationError
from django.core.validators import validate_email
import re

class CreditCardTicketForm(forms.Form):
    email = forms.EmailField(max_length=255, label='Email:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
                             error_messages={'required': 'Please Provide Proper Email',
                                             'invalid': 'Please Enter Valid Email'})
    today = datetime.now().date()
    MONTH_CHOICES = [
        ('1', '01 - January'),
        ('2', '02 - February'),
        ('3', '03 - March'),
        ('4', '04 - April'),
        ('5', '05 - May'),
        ('6', '06 - June'),
        ('7', '07 - July'),
        ('8', '08 - August'),
        ('9', '09 - September'),
        ('10', '10 - October'),
        ('11', '11 - November'),
        ('12', '12 - December'),
    ]
    YEAR_CHOICES = [(y, y) for y in range(today.year, today.year + 21)]
    number = forms.CharField(max_length=255, label='Number:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}),
                             error_messages={'required': 'Please Provide Proper Number without any dash/"-"',
                                             'invalid': 'Please Enter Card Number without Spaces and Dashes'})
    month = forms.ChoiceField(label='Month:',
                              widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Expiry Month'}),
                              choices=MONTH_CHOICES)
    year = forms.ChoiceField(label='Year:',
                             widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Expiry Year'}),
                             choices=YEAR_CHOICES)
    phone = forms.CharField(max_length=255, label='Phone:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
                             error_messages={'required': 'Please Provide Proper Phone',
                                             'invalid': 'Please Enter Valid Phone'})
    # stripe_token = forms.CharField(required=True,widget=forms.HiddenInput())

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        raiseValidation = False

        if re.match(r"\w[\w\.-]*@\w[\w\.-]+\.\w+", email) == None:
            raise forms.ValidationError('Email is not valid')
        if not email:
            raise forms.ValidationError('Enter email address.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address')

        return email



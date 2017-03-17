from django import forms
from datetime import datetime
from .models import Packages, CreditPackages
class CreditCardDepositConfirmForm(forms.Form):

    # name = forms.CharField(label="Name:",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name on card'}),required=True )
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
    number = forms.CharField(max_length=255, label='Number:', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Card Number'}), error_messages={'required': 'Please Provide Proper Number without any dash/"-"', 'invalid': 'Please Enter Card Number without Spaces and Dashes'})
    month = forms.ChoiceField(label='Month:', widget=forms.Select(attrs={'class':'form-control','placeholder':'Expiry Month'}), choices=MONTH_CHOICES)
    year = forms.ChoiceField(label='Year:', widget=forms.Select(attrs={'class':'form-control','placeholder':'Expiry Year'}), choices=YEAR_CHOICES)
    #card_verification = forms.CharField(max_length=255, label="CCV:", widget=forms.TextInput(attrs={'placeholder': 'Card Verification Code','class':'form-control',}), error_messages={'required': 'Enter Security Code - click \"what is this?\" for help','invalid': 'Please Enter Security Number Only'})
    # verification_value = forms.IntegerField(error_messages={'required': 'Enter verification Code','invalid':"Please Enter verification Number Only"},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'CCV'}) , required=True)
    # amount = forms.IntegerField(label='Number:', widget=forms.TextInput(attrs={'class':'form-control',}))

    # def clean_amount(self):
    #     cleaned_data = super(CreditCardDepositConfirmForm, self).clean()
    #     amount = cleaned_data.get("amount")
    #     if amount < 0:
    #         raise forms.ValidationError("Amount has to be greater then or equal to $1.")
    #     return amount


class CreditCardDepositConfirmFormCoin(forms.Form):

    package = forms.ModelChoiceField(label='Package Level',widget=forms.Select(attrs={'class':'form-control m-b'}),queryset=CreditPackages.objects.filter(status=CreditPackages.SHOW).order_by('amount'), required=True, initial=None, empty_label='Please select a package')
    # name = forms.CharField(label="Name:",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name on card'}),required=True )
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
    number = forms.CharField(max_length=255, label='Number:', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Card Number'}), error_messages={'required': 'Please Provide Proper Number without any dash/"-"', 'invalid': 'Please Enter Card Number without Spaces and Dashes'})
    month = forms.ChoiceField(label='Month:', widget=forms.Select(attrs={'class':'form-control','placeholder':'Expiry Month'}), choices=MONTH_CHOICES)
    year = forms.ChoiceField(label='Year:', widget=forms.Select(attrs={'class':'form-control','placeholder':'Expiry Year'}), choices=YEAR_CHOICES)
    #card_verification = forms.CharField(max_length=255, label="CCV:", widget=forms.TextInput(attrs={'placeholder': 'Card Verification Code','class':'form-control',}), error_messages={'required': 'Enter Security Code - click \"what is this?\" for help','invalid': 'Please Enter Security Number Only'})
    # verification_value = forms.IntegerField(error_messages={'required': 'Enter verification Code','invalid':"Please Enter verification Number Only"},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'CCV'}) , required=True)
    # amount = forms.IntegerField(label='Number:', widget=forms.TextInput(attrs={'class':'form-control',}))

    # def clean_amount(self):
    #     cleaned_data = super(CreditCardDepositConfirmForm, self).clean()
    #     amount = cleaned_data.get("amount")
    #     if amount < 0:
    #         raise forms.ValidationError("Amount has to be greater then or equal to $1.")
    #     return amount

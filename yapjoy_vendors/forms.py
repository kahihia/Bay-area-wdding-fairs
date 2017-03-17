from django import forms
from yapjoy_s3direct.widgets import S3DirectWidget
from yapjoy_vendors.models import VendorRegistration, VendorImage
from yapjoy_registration.models import UserProfile
from django.db.models import Q
class messageForm(forms.Form):
    # subject = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Subject Title'}), required=True, error_messages={'required':'Subject is required.'})
    message = forms.CharField(max_length=1500, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Write your message here'}), required=True, error_messages={'required':'Message is required.'})
    images = forms.URLField(widget=S3DirectWidget(dest='imgs'), required=False)

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'First Name'}),
                              required=True, error_messages={'required': 'Subject is required.'})

    last_name = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
                                 required=True, error_messages={'required': 'Subject is required.'})

    company_name = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
                                 required=False)

    phone_number = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
                                 required=False)

    contact_email = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Email'}),
                                   required=True, error_messages={'required': 'Subject is required.'})

    website_url = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
                                   required=False)

    business_location = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Location'}),
                                  required=False)

    state = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
                                        required=False)

    zip = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip code'}),
                            required=False)

    # category = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}), required=False)

    # options = optionsSearch.objects.all().values_list('name', flat=True)['name']
    OPTIONS = (
        ("video", "Video"),
        ("catering", "Catering"),
    )
    category = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS, required=False)

    # second_category = forms.BooleanField(required=False)
from yapjoy_registration.models import optionsSearch
class StoreFront(forms.ModelForm):
    website_url = forms.CharField()
    categories = forms.ModelChoiceField(queryset=optionsSearch.objects.filter(status=optionsSearch.SHOW), required=True)
    class Meta:
        model = VendorRegistration
        exclude = ['code','verification_code','created_at','modified_at','user','status','website_url']

    def clean_email(self):
        cleaned_data = super(StoreFront, self).clean()
        email = self.cleaned_data.get('email')
        if VendorRegistration.objects.filter(Q(user__email__iexact=email)|Q(user__username__iexact=email)).exists():
            raise forms.ValidationError('Email is already registered with YapJoy.')
        return email

    def __init__(self, *args, **kwargs):
        super(StoreFront, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

class StoreFrontEditForm(forms.ModelForm):
    # categories = forms.ModelChoiceField(queryset=optionsSearch.objects.filter(status=optionsSearch.SHOW), required=True)
    class Meta:
        model = VendorRegistration
        exclude = ['code','verification_code','created_at','modified_at','user','email','status','categories','business_location','state','zip','company_name','website_url']

    # def clean_email(self):
    #     cleaned_data = super(StoreFront, self).clean()
    #     email = self.cleaned_data.get('email')
    #     if VendorRegistration.objects.filter(Q(user__email__iexact=email)|Q(user__username__iexact=email)).exists():
    #         raise forms.ValidationError('Email is already registered with YapJoy.')
    #     return email

    def __init__(self, *args, **kwargs):
        super(StoreFrontEditForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

class VerifyEmailCode(forms.Form):
    code = forms.CharField(max_length=6)
    # def clean_code(self):
    #     cleaned_data = super(VerifyEmailCode, self).clean()
    #     code = self.cleaned_data.get('code')
    #     return code

class SetupPasswordForm(forms.Form):
    password = forms.CharField(required=True)
    # def clean_code(self):
    #     cleaned_data = super(VerifyEmailCode, self).clean()
    #     code = self.cleaned_data.get('code')
    #     return code
    def clean_password(self):
        cleaned_data = super(SetupPasswordForm, self).clean()
        password = self.cleaned_data.get('password')
        if len(password) < 7:
            raise forms.ValidationError('Password should atleast have 7 digits.')
        return password

class vendorImageForm(forms.ModelForm):
    class Meta:
        model = VendorImage
        fields = ['image']
    # image = forms.ImageField()

class VendorProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

class vendorVideoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['video']
    # image = forms.ImageField()

#
# class RegistrationForm(forms.Form):
#     name = forms.CharField()

from django import forms
from s3direct.widgets import S3DirectWidget

class S3DirectUploadForm(forms.Form):
    video = forms.URLField(widget=S3DirectWidget(dest='vids'))
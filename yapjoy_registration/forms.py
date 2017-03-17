__author__ = 'Adeel'
from django import forms
from .models import UserProfile, RegisterRequest
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import RegexValidator, ValidationError
from yapjoy_registration.commons import WydlWrapper
from .models import UserProfile, Company
from django.db.models import Q
from django.utils.translation import ugettext, ugettext_lazy as _
from yapjoy_s3direct.widgets import S3DirectWidget

class DeleteConfirmForm(forms.Form):
    password = forms.CharField(error_messages={'required': 'Password is required'}, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password'}))

class loginForm(forms.Form):
    username = forms.CharField(error_messages={'required': 'Email is required'}, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Email'}))
    password = forms.CharField(error_messages={'required': 'Password is required'}, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter Password'}))

    # def clean_username(self):
    #     cleaned_data = super(loginForm, self).clean()
    #     username = cleaned_data.get("username")
    #     if User.objects.filter(email__iexact=username).count() < 1:
    #         raise forms.ValidationError('Email/Password is not correct.')
    #     if User.objects.filter(email__iexact=username, is_active=False) < 1:
    #         raise forms.ValidationError('Account is not active.')
    #     return username

class feedbackForm(forms.Form):
    subject = forms.CharField(required=True,error_messages={'required': 'Subject is required'}, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Subject'}))
    message = forms.CharField(required=True,error_messages={'required': 'Message is required'}, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Enter Message'}))

class supportForm(forms.Form):
    CHOICES = [
                ('Excited', 'Excited'),
                ('Confused', 'Confused'),
                ('Worried', 'Worried'),
                ('Upset', 'Upset'),
                ('Panicked', 'Panicked'),
                ('Angry', 'Angry'),
    ]

    # CHOICES_STATES = (
    #     ('','-----------'),
    #     STATE_CHOICES,
    # )
    subject = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=CHOICES, error_messages={'required': 'Please choose a state'})

    # subject = forms.CharField(required=True,error_messages={'required': 'Subject is required'}, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter Subject'}))
    message = forms.CharField(required=True,error_messages={'required': 'Message is required'}, widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Enter Message'}))

# class profileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['gender','']

class RegisterRequestForm(forms.ModelForm):
    class Meta:
        model = RegisterRequest
        fields = ['name','email','wedding_date','wedding_location']

    def __init__(self, *args, **kwargs):
        super(RegisterRequestForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].widget = forms.TextInput(attrs={'placeholder':'Email Address'})
        self.fields['name'].widget = forms.TextInput(attrs={'placeholder':'Name'})
        self.fields['wedding_date'].widget = forms.TextInput(attrs={'placeholder':'Wedding Date'})
        self.fields['wedding_location'].widget = forms.TextInput(attrs={'placeholder':'Wedding Location'})
        # self.fields['password'].required = True

    # def clean_email(self):
    #     self.email = self.cleaned_data['email']
    #     if RegisterRequest.objects.filter(email__iexact=self.email).exists():
    #         raise ValidationError('You already have a request with this email.')

class emailEditForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': 'Email is required'}, widget=forms.TextInput(attrs={'class':'form-control'}))

    def clean_email(self):
        cleaned_data = super(emailEditForm, self).clean()
        email = cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).count() >= 1:
            raise forms.ValidationError('Email already exist.')
        return email

class yelpForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['yelp_location_zip','yelp_name',]

class passwordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),max_length=100, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}),max_length=100, required=True)

    def clean_confirm_password(self):
        cleaned_data = super(passwordForm, self).clean()
        confirm_password = self.cleaned_data.get('confirm_password')
        password = cleaned_data.get('password')
        print password, confirm_password
        if password and confirm_password and password == confirm_password:
            pass
        else:
            raise forms.ValidationError('Passwords do not match.')
from localflavor.us.models import USStateField
from localflavor.us.us_states import STATE_CHOICES
class profileForm(forms.ModelForm):
    CHOICES=[('m','Male'),
         ('f','Female')]

    # CHOICES_STATES = (
    #     ('','-----------'),
    #     STATE_CHOICES,
    # )
    gender = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    state = forms.ChoiceField(choices=[[0, 'Select State']]+list(STATE_CHOICES))
    class Meta:
        model = UserProfile
        fields = ['wedding_date','image','cover_image','age','looking_for','street','city','zip','budget','wedding_location']
        widgets = {
                   'wedding_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':''}),
                   'street': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Street'}),
                   'city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}),
                   # 'state': forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}),
                   'zip': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zip'}),
                   # 'field2': forms.TextInput(attrs={'class':'textInputClass', 'placeholder':'Enter a Value..', 'readonly':'readonly', 'value':10}),
                   'looking_for': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Use tags/keywords which describes your interest', 'rows':3}),

               }

    def __init__(self, *args, **kwargs):
        super(profileForm, self).__init__(*args, **kwargs)
        self.fields['budget'].required = False
        self.fields['gender'].required = False
        # self.fields['looking_for'].required = False

class companyForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Company Name'}))
    class Meta:
        model = Company
        fields = ['description','payment_terms','employees']
        widgets = {
                   # 'wedding_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':'Wedding Date'}),
                  # 'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Company Name'}),
                   # 'city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}),
                   # # 'state': forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}),
                   # 'zip': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zip'}),
                   # 'field2': forms.TextInput(attrs={'class':'textInputClass', 'placeholder':'Enter a Value..', 'readonly':'readonly', 'value':10}),
                   'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Company Description', 'rows':3}),
                   'payment_terms': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Payment Terms', 'rows':3}),
                   #'employees': forms.ChoiceField(attrs={'class':'form-control'}),

               }

class privacy(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notification_events','notification_tasks']

class profileUpdateForm(forms.ModelForm):
    CHOICES=[('m','Male'),
         ('f','Female')]

    gender = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), required=False)

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    state = forms.ChoiceField(choices=[[0, 'Select State']]+list(STATE_CHOICES))
    class Meta:
        model = UserProfile
        fields = ['wedding_date','age','looking_for','street','city','zip']
        widgets = {
                   'wedding_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':'Wedding Date'}),
                   'street': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Street'}),
                   'city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}),
                   # 'state': forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}),
                   'zip': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zip'}),
                   # 'field2': forms.TextInput(attrs={'class':'textInputClass', 'placeholder':'Enter a Value..', 'readonly':'readonly', 'value':10}),
                   'looking_for': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Use tags/keywords which describes your interest', 'rows':3}),

               }
    def __init__(self, *args, **kwargs):
        super(profileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['wedding_date'].required = True
        # self.fields['looking_for'].required = True

class profileProfessionalForm(forms.ModelForm):
    CHOICES=[('m','Male'),
         ('f','Female')]

    gender = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), required=False)

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    class Meta:
        model = UserProfile
        fields = ['age','looking_for','image','cover_image']
        widgets = {
                   'looking_for': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Services & Products', 'rows':3}),

               }

class ProfileSelectForm(forms.Form):
    GROOM = "Groom"
    BRIDE = "Bride"
    PROFESSIONAL = "Professional"
    OTHER = "Other"
    TYPE_CHOICES = (
        (OTHER, "Other"),
        (GROOM, "Groom"),
        (BRIDE, "Bride"),
        (PROFESSIONAL, "Wedding Professional (Vendor)"),
    )
    type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES, initial=OTHER,error_messages={'required': 'Please choose a type'})

class ProfileCreateForm(forms.ModelForm):
    GROOM = "Groom"
    BRIDE = "Bride"
    PROFESSIONAL = "Professional"
    OTHER = "Other"
    TYPE_CHOICES = (
        (OTHER, "Other"),
        (GROOM, "Groom"),
        (BRIDE, "Bride"),
        (PROFESSIONAL, "Wedding Professional (Vendor)"),
    )
    type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES, initial=OTHER,error_messages={'required': 'Please choose a type'})
    class Meta:
        model = User
        fields = ['email', 'password','first_name','last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileCreateForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password'].required = True
        self.fields['type'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError(_("Email already exist, choose another one."))
        return email


class NewRegForm(forms.Form):
    GROOM = "Groom"
    BRIDE = "Bride"
    PROFESSIONAL = "Professional"
    OTHER = "Other"
    EVENTMANAGER = "Event"
    TYPE_CHOICES = (
        (BRIDE, "Bride"),
        (GROOM, "Groom"),
        (PROFESSIONAL, "Wedding Professional (Vendor)"),
        # (EVENTMANAGER, "Event Manager"),
        (OTHER, "Other"),
    )
    type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES,error_messages={'required': 'Please choose a type'})
    first_name = forms.CharField(error_messages={'required': 'Please enter First Name'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(error_messages={'required': 'Please enter Last Name'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    email = forms.EmailField(error_messages={'required': 'Please enter the Email'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(error_messages={'required': 'Please enter the password'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password = forms.CharField(error_messages={'required': 'Please enter the Password again'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    agree = forms.BooleanField(required=True)

    def clean_confirm_password(self):
        cleaned_data = super(NewRegForm, self).clean()
        confirm_password = self.cleaned_data.get('confirm_password')
        password = cleaned_data.get('password')
        print password, confirm_password
        if password and confirm_password and password == confirm_password:
            pass
        else:
            raise forms.ValidationError('Passwords do not match.')
        return password

    def clean_email(self):
        cleaned_data = super(NewRegForm, self).clean()
        email = cleaned_data.get("email")
        user = User.objects.filter(Q(email__iexact=email)|Q(username__iexact=email))
        if user.count() > 0:
            raise ValidationError("Email already exist.")
        return email


class NewRegForm2(forms.Form):
    GROOM = "Groom"
    BRIDE = "Bride"
    PROFESSIONAL = "Professional"
    OTHER = "Other"
    EVENTMANAGER = "Event"
    TYPE_CHOICES = (
        (BRIDE, "Bride"),
        (GROOM, "Groom"),
        (PROFESSIONAL, "Wedding Professional (Vendor)"),
        # (EVENTMANAGER, "Event Manager"),
        (OTHER, "Other"),
    )
    # type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES,error_messages={'required': 'Please choose a type'})
    name = forms.CharField(error_messages={'required': 'Please enter Name'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}))
    # last_name = forms.CharField(error_messages={'required': 'Please enter Last Name'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    email = forms.EmailField(error_messages={'required': 'Please enter the Email'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(error_messages={'required': 'Please enter the password'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    # confirm_password = forms.CharField(error_messages={'required': 'Please enter the Password again'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    # agree = forms.BooleanField(required=True)
    #
    # def clean_confirm_password(self):
    #     cleaned_data = super(NewRegForm, self).clean()
    #     confirm_password = self.cleaned_data.get('confirm_password')
    #     password = cleaned_data.get('password')
    #     print password, confirm_password
    #     if password and confirm_password and password == confirm_password:
    #         pass
    #     else:
    #         raise forms.ValidationError('Passwords do not match.')
    #     return password

    def clean_email(self):
        cleaned_data = super(NewRegForm2, self).clean()
        email = cleaned_data.get("email")
        user = User.objects.filter(Q(email__iexact=email)|Q(username__iexact=email))
        if user.count() > 0:
            raise ValidationError("Email already exist.")
        return email


class subscriptionForm(forms.Form):

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



class PasswordResetForm(forms.Form):

    email = forms.EmailField(error_messages={'required': 'Please enter the Email'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))

    def clean_email(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        email = cleaned_data.get("email")
        user = User.objects.filter(Q(email__iexact=email)|Q(username__iexact=email))
        if user.count() <= 0:
            raise ValidationError("Email does not exist.")
        return email

class Passowrd_reset_form(forms.Form):

    email = forms.EmailField(required=True, error_messages={'required': 'Enter the Email'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(required=True, error_messages={'required': 'Enter the password'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password = forms.CharField(required=True, error_messages={'required': 'Enter the password again'},widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))

    def clean_confirm_password(self):
        cleaned_data = super(Passowrd_reset_form, self).clean()
        confirm_password = self.cleaned_data.get('confirm_password')
        password = cleaned_data.get('password')
        print password, confirm_password
        if password and confirm_password and password == confirm_password:
            print 'both the passwords are equal'
        else:
            raise forms.ValidationError('Passwords do not match.')
        return password

    def clean_email(self):
        cleaned_data = super(Passowrd_reset_form, self).clean()
        email = cleaned_data.get("email")
        user = User.objects.filter(Q(email__iexact=email)|Q(username__iexact=email))
        if user.count() < 0:
            raise ValidationError("Email does not exist.")
        return email

class imageForm(forms.Form):
    images = forms.URLField(widget=S3DirectWidget(dest='imgs'))

class companySettingsForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Company Name'}))
    street = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Street'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'City'}))
    state = forms.ChoiceField(choices=[[0, 'Select State']]+list(STATE_CHOICES), required=True)
    zip = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Zip'}))
    phone = forms.CharField(required=True)
    class Meta:
        model = Company
        fields = ['description','payment_terms','employees']
        widgets = {
                   # 'wedding_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':'Wedding Date'}),
                  # 'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Company Name'}),
                   # 'city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}),
                   # # 'state': forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}),
                   # 'zip': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zip'}),
                   # 'field2': forms.TextInput(attrs={'class':'textInputClass', 'placeholder':'Enter a Value..', 'readonly':'readonly', 'value':10}),
                   'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Company Description', 'rows':3}),
                   'payment_terms': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Payment Terms', 'rows':3}),
                   #'employees': forms.ChoiceField(attrs={'class':'form-control'}),

               }

class registrationWizard(forms.Form):
    GROOM = "Groom"
    BRIDE = "Bride"
    # PROFESSIONAL = "Professional"
    # OTHER = "Other"
    # EVENTMANAGER = "Event"
    # UNKNOWNPROFILE = "Unknown"




    TYPE_CHOICES = (
        # (OTHER, "Other"),
        (BRIDE, "Bride"),
        (GROOM, "Groom"),
        # (PROFESSIONAL, "Wedding Professional"),
        # (EVENTMANAGER, "Event Manager"),
        # (UNKNOWNPROFILE, "Unknown Profile"),
    )
    # class Meta:
    #     model = UserProfile
    #     fields = ['type']

    type = forms.ChoiceField(choices=TYPE_CHOICES, required=True)

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),max_length=100, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}),max_length=100, required=True)

    def clean_confirm_password(self):
        cleaned_data = super(registrationWizard, self).clean()
        confirm_password = self.cleaned_data.get('confirm_password')
        password = cleaned_data.get('password')
        print password, confirm_password
        if password and confirm_password and password == confirm_password:
            pass
        else:
            raise forms.ValidationError('Passwords do not match.')
class ProfileFormNew(forms.ModelForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    # email = forms.EmailField(max_length=255)

    class Meta:
        model = UserProfile
        fields = ['image','profession','phone']
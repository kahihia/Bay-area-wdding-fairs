from django import forms
from .models import *
from yapjoy_registration.models import UserProfile
import csv, urllib2
from yapjoy.settings import *
from django.forms import ModelForm
from datetime import datetime
from django.core.validators import ValidationError
from django.core.validators import validate_email
import re
def day_month_pad_0(in_str):
    if len(in_str) == 1:
        out_str = "0"+(in_str)
    else:
        out_str = in_str

    return out_str

def year_padd(in_str):
    if len(in_str) == 4:
        year = in_str
    elif len(in_str) > 0:
        year = "20"+in_str
    else:
        year = 0
    return year

def date_format_1(in_date):
    in_list = in_date.split('-')
    # print "format 1 "+str(in_list)
    date_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",\
                 "Jul": '07', "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    if len(in_list[0]) == 3:
        try: day = day_month_pad_0(in_list[1])
        except: day = 0
        try: month = date_dict[in_list[0]]
        except: month = ""
    else:
        try: day = day_month_pad_0(in_list[0])
        except: day = 0
        try: month = date_dict[in_list[1]]
        except: month = ""

    try:
        year = year_padd(in_list[2])
    except:
        year = 0
    return year, month, day


def date_format_2(in_date):
    in_list = in_date.split('/')
    # print "format 2 "+str(in_list)

    if len(in_list[0]) == 1:
        month = "0"+(in_list[0])
        day = day_month_pad_0(in_list[1])
    elif int(in_list[0]) > 12:
        month = day_month_pad_0(in_list[1])
        day = in_list[0]
    else:
        month = in_list[0]
        day = day_month_pad_0(in_list[1])

    try:
        year = year_padd(in_list[2])
    except:
        year = 0
    return year, month, day

def date_wrapper(*args):
    year, month, day = args[0]

    if str(month).isdigit() and str(year).isdigit() and str(day).isdigit():
        if int(day) > 31 or int(month) > 12 or year == 0 or len(year) > 4:
            # print " out is 0"
            out_date = 0
        else:
            out_date = year+"-"+month+"-"+day
    else:
        out_date = 0

    return out_date

def convert_date(in_date):
    #covert m/d/yy to yyyy-mm-dd
    if "-" in in_date:
        out_date = date_wrapper(date_format_1(in_date))
    elif "/" in in_date:
        out_date = date_wrapper(date_format_2(in_date))
    else:
        out_date = 0

    return out_date

def fn_save_userinfo(row, csvfile):
    #for vendor interested in
    # row_11 = row[11].replace('\r\n', ',')
    wedding_date = convert_date(row[12])
    email = str(row[1])
    try:
        userprofile_id = UserProfile.objects.select_related('user').filter(user__email=email)[0]
    except:
        userprofile_id = 0

    try:
        UserInfo.objects.get(Email=email)
        print "already "+str(row[0])
    except:
        print "save "+str(row[0])
        if wedding_date == 0:
            UserInfo.objects.create(\
                csvfile=csvfile,\
                LastName=str(row[0]),\
                Email=email,\
                MailingStreet=str(row[2]),\
                MailingCity=str(row[3]),\
                OtherCity=str(row[4]),\
                MailingState=str(row[5]),\
                MailingZip=str(row[6]),\
                BridesFirstName=str(row[7]),\
                BridesLastName=str(row[8]),\
                WeddingLocation=str(row[9]),\
                Budget=str(row[10]),\
                VendorInterestedIn=str(row[11]),\
                userprofileID=userprofile_id
                )
        else:
            UserInfo.objects.create(\
                csvfile=csvfile,\
                LastName=str(row[0]),\
                Email=email,\
                MailingStreet=str(row[2]),\
                MailingCity=str(row[3]),\
                OtherCity=str(row[4]),\
                MailingState=str(row[5]),\
                MailingZip=str(row[6]),\
                BridesFirstName=str(row[7]),\
                BridesLastName=str(row[8]),\
                WeddingLocation=str(row[9]),\
                Budget=str(row[10]),\
                VendorInterestedIn=str(row[11]),\
                WeddingDate=wedding_date,\
                userprofileID=userprofile_id
                )



def read_csv_from_url(file_name, id):
    #read from S3 url
    file_url = MEDIA_URL+'media/'+str(file_name)

    try:
        response = urllib2.urlopen(file_url)
        rows = list(csv.reader(response.read().splitlines()))[1:]
        # print rows[0]
        csvfile = CSVFile.objects.get(id=id)

        # for x in rows:
        #     print x
        #     fn_save_userinfo(x, id)

    except:
        rows = []
        csvfile = []
        print "didn't get any"


    # fn_save_userinfo(rows[1137], csvfile)
    # new_rows = rows[3035:]
    map(lambda x: fn_save_userinfo(x, csvfile), rows)

def read_csv_row_from_db(csvFile):
    try:
        csv_obj = CSVFile.objects.get(csvfile='media/'+str(csvFile))
        # print csv_obj.csvfile

        try:
            userInfo_rows = UserInfo.objects.filter(csvfile=csv_obj.id)
        except:
            userInfo_rows = []

    except:
        userInfo_rows = []

    return userInfo_rows

class UserInfoForm(forms.Form):
    #Save to S3 bucket
    csvFile = forms.FileField()
    # picture = forms.ImageField()

    # def take_csv_file(self):
    #     #1.read when loading
    #     file = self.clean_data['csvFile']
    #
    #     #2.from local testing only
    #     # file = os.path.join(settings.ROOT_PATH, 'B_G_List.csv')
    #
    #     #"rU" for Mac file
    #     try:
    #         f = open(file, "rU")
    #         rows = list(csv.reader(f.read().splitlines()))
    #         print rows[8]
    #         map(lambda x: fn_save_userinfo(x, id), rows[1:])
    #     except:
    #         pass


    # class Meta:
    #     model = UserInfo
    #     fields = ['LastName','Email','MailingStreet', 'MailingCity', 'OtherCity', 'MailingState', 'MailingZip',\
    #               'BridesFirstName', 'BridesLastName', 'WeddingLocation', 'Budget', 'VendorInterestedIn', 'Wedding_date']
    #
    #     widgets = {
    #         'LastName': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'LastName'}),
    #         'Email': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    #         'MailingStreet': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'MailingStreet'}),
    #         'MailingCity': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'MailingCity'}),
    #         'OtherCity': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'OtherCity'}),
    #         'MailingState': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'MailingState'}),
    #         'MailingZip': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'MailingZip'}),
    #         'BridesFirstName': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'BridesFirstName'}),
    #         'BridesLastName': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'BridesLastName'}),
    #         'WeddingLocation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'WeddingLocation'}),
    #         'Budget': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Budget'}),
    #         'VendorInterestedIn': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'VendorInterestedIn'}),
    #         'Wedding_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Wedding_date'}),
    #     }

class WpInfoForm(forms.Form):
    firstname = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'First Name is required.'})

    lastname = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'Last Name is required.'})

    date = forms.DateTimeField(required=True,widget=forms.TextInput(attrs={'class': 'form-control hasDatepicker',}),
                               error_messages={'required': 'Date is required.'})

    email = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'Event is required.'})

    amount = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'0'}))

    # accept = forms.BooleanField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', }))
    accept = forms.BooleanField(required=False)

    # class Meta:
    #     model = WpInfo
    #     fields = ['firstname', 'lastname', 'date', 'event', 'email', 'amount']

    def clean_amount(self):
        cleaned_data = super(WpInfoForm, self).clean()
        amount = self.cleaned_data.get('amount')
        print "debug"+str(amount)
        try:
            amount = int(amount)
        except:
            raise forms.ValidationError('Amount can only be integers.')
        return amount


class LasVegasForm(forms.Form):
    firstName = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'First Name is required.'})

    lastName = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'Last Name is required.'})

    email = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'Email is required.'})

    weddingDate = forms.DateField()


class registration_event_form(forms.ModelForm):
    # event = forms.ModelChoiceField(
    #     queryset=Event_fairs.objects.filter(is_expired=False),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=True,
    # )
    commission = forms.FloatField(required=False)
    how_heard = forms.ChoiceField(label='How Heard:', widget=forms.Select(
        attrs={'class': 'form-control', 'placeholder': 'How did you hear'}), choices=Register_Event.HEARD_CHOICES,
                                  initial="How did you hear?")
    EVERYTHING = "EVERYTHING"
    PHOTO = "Photography"
    VIDEO = "Videography"
    HEALTH_FITNESS = "Health & Fitness"
    FLORAL_DESIGN = "Florists"
    CAKE = "Cake"
    WEDDING_PLANNER = "Planner"
    VENUE = 'Venue'
    HAIR_MAKEUP = "Hair & Make up"
    DJ = "DJ"
    LIGHTING = "Lighting"
    GIFT = "Favors & Decor"
    CATERER = "Caterer"
    RING = "Jewelry"
    BRIDE_DRESS = "Bridal Wear"
    GROOM_SUIT = "Menswear"
    LIMO = "Limo"
    INVITATION = "Invitation"
    OTHERS = "Other(Please mention below)"

    CATEGORY_OPTIONS = (
        # (EVERYTHING, "EVERYTHING"),
        ("", "Business Category"),
        (PHOTO, "Photography"),
        (VIDEO, "Videography"),
        (HEALTH_FITNESS, "Health & Fitness"),
        (FLORAL_DESIGN, "Florists"),
        (CAKE, "Cake"),
        (WEDDING_PLANNER, "Planner"),
        (VENUE, 'Venue'),
        (HAIR_MAKEUP, "Hair & Make up"),
        (DJ, "DJ"),
        (LIGHTING, "Lighting"),
        (GIFT, "Favors & Decor"),
        (CATERER, "Caterer"),
        (RING, "Jewelry"),
        (BRIDE_DRESS, "Bridal Wear"),
        (GROOM_SUIT, "Menswear"),
        (LIMO, "Limo"),
        (INVITATION, "Invitation"),
        (OTHERS, "Other (Please mention below)"),
    )
    categories = forms.ChoiceField(choices=CATEGORY_OPTIONS,
                                           initial='Select Category')

    class Meta:
        model = Register_Event
        exclude = ["created_at", "modified_at", "event", "user", "status", "sales", 'type', 'is_lasVegasSignIn','categories']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name*'}),
            'business_name': forms.TextInput(attrs={'placeholder': 'Business Name*'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone*'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email*'}),
            'city': forms.TextInput(attrs={'placeholder': 'City*'}),
            'website': forms.TextInput(attrs={'placeholder': 'Website'}),
            'zip': forms.TextInput(attrs={'placeholder': 'Zip Code*'}),
            'amount_due': forms.Textarea(attrs={'placeholder': 'Amount Due'}),
            # 'commission': forms.TextInput(attrs={'placeholder': 'Commission'}),
            # 'booth': for,
            # 'is_fashionshow': forms.Textarea(attrs={'placeholder': 'is Fashionshow'}),
        }

    def __init__(self, *args, **kwargs):
        super(registration_event_form, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['business_name'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['city'].required = True
        self.fields['zip'].required = True
        self.fields['comments'].required = False
        self.fields['how_heard'].required = True
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Please Select"
        self.fields['categories'].required = True
        self.fields['amount_due'].required = False
        self.fields['payment_method'].required = False
        self.fields['description'].required = False
        self.fields['weddingDate'].required = False
        self.fields['is_fashionshow'].required = False
        self.fields['is_partner_vendor'].required = False
        self.fields['booth'].required = False
        self.fields['food'].required = False
        self.fields['booth'].empty_label = "Please select"
        self.fields['food'].empty_label = "Please select"
        self.fields['commission'].required = False
        self.fields['website'].required = False

class bg_registration_form(forms.ModelForm):
    firstName = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name*'}),
                              required=True, error_messages={'required': 'First Name is required.'})

    lastName = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name*'}),
                              required=True, error_messages={'required': 'Last Name is required.'})
    how_heard = forms.ChoiceField(label='How Heard:', widget=forms.Select(attrs={'class':'form-control','placeholder':'How did you hear'}), choices=Register_Event.HEARD_CHOICES, initial="How did you hear?")
    categories=forms.MultipleChoiceField(choices=CategoryOptions.CATEGORY_OPTIONS,widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Register_Event
        exclude = ["created_at", "modified_at", "event", "user", "category", "name",
                   "business_name", "amount_due", "payment_method", "description"
                   "status", "sales", 'type', 'is_lasVegasSignIn',"categories",'how_heard']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Phone*'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email*'}),
            'city': forms.TextInput(attrs={'placeholder': 'City*'}),
            'zip': forms.TextInput(attrs={'placeholder': 'Zip Code*'}),
            'weddingDate': forms.TextInput(attrs={'placeholder': 'Wedding Date mm/dd/yyy (if applicable)'}),
        }

    def __init__(self, *args, **kwargs):
        super(bg_registration_form, self).__init__(*args, **kwargs)
        # self.fields['name'].required = False
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['city'].required = True
        self.fields['zip'].required = False
        self.fields['comments'].required = False
        self.fields['how_heard'].required = True
        self.fields['how_heard'].initial = "How did you hear?"
        self.fields['categories'].required = True
        self.fields['commission'].required = False
        self.fields['weddingDate'].required = False


class contractor_detail_note_form(forms.ModelForm):
    class Meta:
        model = Notes
        exclude = ["created_at", "modified_at", "exhibitor", 'note_writer']
        widgets = {
            'note': forms.Textarea(attrs={'placeholder': 'Notes', 'rows': 4, 'cols': 20}),
        }

    def __init__(self, *args, **kwargs):
        super(contractor_detail_note_form, self).__init__(*args, **kwargs)
        self.fields['note'].required = True

class events_search_form(forms.Form):
    events = forms.ModelChoiceField(queryset=Event_fairs.objects.all().order_by('-date'))


class sales_tasks_form(forms.ModelForm):
    class Meta:
        model = SalesTasks
        exclude = ["created_at", "modified_at", "exhibitor","sales"]
        widgets = {
            # 'subject': forms.TextInput(attrs={'placeholder': 'Subject*'}),
            'message': forms.Textarea(attrs={'placeholder': 'Tasks', 'rows': 4}),
            # 'sales': forms.ModelChoiceField(required=True,
            #         widget=forms.CheckboxSelectMultiple, queryset=User.objects.filter(is_superuser=True))

            # 'dueDate': forms.DateTimeField(required=True, widget=forms.TextInput(
            #     attrs={'class': 'form-control hasDatepicker',}),
            #                    error_messages={'required': 'Date is required.'}),
        }

    def __init__(self, *args, **kwargs):
        super(sales_tasks_form, self).__init__(*args, **kwargs)
        self.fields['subject'].required = True
        self.fields['message'].required = True
        self.fields['dueDate'].required = True
        self.fields['status'].required = True
        # self.fields['sales'].query = User.objects.filter(is_staff=True)

class CreditCardForm(forms.Form):

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
    agree = forms.BooleanField(required=True)
    # def clean_amount(self):
    #     cleaned_data = super(CreditCardDepositConfirmForm, self).clean()
    #     amount = cleaned_data.get("amount")
    #     if amount < 0:
    #         raise forms.ValidationError("Amount has to be greater then or equal to $1.")
    #     return amount

class checkForm(forms.Form):
    agree = forms.BooleanField(required=True)

class CreditCardCreationForm(forms.Form):

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
    # agree = forms.BooleanField(required=True)
    # def clean_amount(self):
    #     cleaned_data = super(CreditCardDepositConfirmForm, self).clean()
    #     amount = cleaned_data.get("amount")
    #     if amount < 0:
    #         raise forms.ValidationError("Amount has to be greater then or equal to $1.")
    #     return amount


class InvoiceCreationForm(forms.ModelForm):
    class Meta:
        model = Invoice_Event
        fields = ['amount','notes','prize','is_sent']

    def __init__(self, *args, **kwargs):
        super(InvoiceCreationForm, self).__init__(*args, **kwargs)
        self.fields['amount'].required = True
        self.fields['prize'].required = True
        self.fields['notes'].required = True
        self.fields['notes'].required = False

    def clean_amount(self):
        cleaned_data = super(InvoiceCreationForm, self).clean()
        amount = self.cleaned_data.get('amount')
        try:
            amount = int(amount)
            # if amount < 1:
            #     raise forms.ValidationError('Amount cannot be less then 1.')
        except Exception as e:
            print e
            raise forms.ValidationError('Amount can only be integers.')
        return amount

class SearchForm(forms.Form):
    email = forms.CharField(required=True)

    # def clean_email(self):
    #     cleaned_data = super(SearchForm, self).clean()
    #     email = self.cleaned_data.get('email')


class DateForm(forms.Form):
    date_deposit = forms.DateField(required=False)
    date_balance1 = forms.DateField(required=False)
    date_balance2 = forms.DateField(required=False)
    date_balance3 = forms.DateField(required=False)

class InvoiceCreationBulkForm(forms.ModelForm):
    invoice_events = forms.ModelMultipleChoiceField(required=False,
        widget=forms.CheckboxSelectMultiple, queryset=Invoice_Event.objects.filter(is_sent=False))
    class Meta:
        model = BulkInvoices
        fields = ['email']

    # def __init__(self, *args, **kwargs):
    #     super(InvoiceCreationForm, self).__init__(*args, **kwargs)
    #     self.fields['amount'].required = True
    #     self.fields['prize'].required = True
    #     self.fields['notes'].required = True
    #     self.fields['notes'].required = False
    #
    # def clean_amount(self):
    #     cleaned_data = super(InvoiceCreationForm, self).clean()
    #     amount = self.cleaned_data.get('amount')
    #     try:
    #         amount = int(amount)
    #         # if amount < 1:
    #         #     raise forms.ValidationError('Amount cannot be less then 1.')
    #     except Exception as e:
    #         print e
    #         raise forms.ValidationError('Amount can only be integers.')
    #     return amount


class InvoiceForm_BulkCreate(forms.Form):
    events = forms.ModelChoiceField(queryset=Register_Event.objects.all())


    list_price = forms.IntegerField(required=False)
    offered_price = forms.IntegerField(required=True)
    pv_prize_offered = forms.CharField(required=False)

    CC = "CreditCard"
    CHECK = "Check"
    CASH = "Cash"
    TYPE_CHOICES = (
        (CC, "Credit Card"),
        (CHECK, "Check"),
        (CASH, "cash"),
    )

    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES, initial=CC,error_messages={'required': 'Please choose a payment method'})
    AMOUNT = "Amount"
    COMP = "Comp"
    NONE = "N"
    ELECTRICITY_CHOICES = (
        (AMOUNT, "$75"),
        (COMP, "Comp"),
        (NONE, "None"),
    )

    electricity_types = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=ELECTRICITY_CHOICES, initial=AMOUNT,error_messages={'required': 'Please choose an electricity method'})
    email_list = forms.ModelChoiceField(error_messages={'required': 'Select an email list'},label='Email List',widget=forms.Select(attrs={'class':'form-control m-b'}),queryset=csvUpload.objects.all().order_by('created_at'), initial=None, empty_label='Please select a list', required=False)

    def __init__(self, email, *args, **kwargs):
        super(InvoiceForm_BulkCreate, self).__init__(*args, **kwargs)
        self.fields['events'].queryset = Register_Event.objects.filter(user__email=email).order_by('-created_at')
        print "Form Initial Email: ",email

class InvoiceForm(forms.Form):
    list_price = forms.IntegerField(required=False)
    offered_price = forms.IntegerField(required=True)
    pv_prize_offered = forms.CharField(required=False)
    # deposit = forms.IntegerField(required=True)
    # send_email_now = forms.BooleanField(required=False)
    # balance1 = forms.IntegerField(required=True)
    # balance2 = forms.IntegerField(required=True)
    # balance3 = forms.IntegerField(required=True)
    # date_deposit = forms.DateField()
    # date_balance1 = forms.DateField()
    # date_balance2 = forms.DateField()
    # date_balance3 = forms.DateField()

    CC = "CreditCard"
    CHECK = "Check"
    CASH = "Cash"
    TYPE_CHOICES = (
        (CC, "Credit Card"),
        (CHECK, "Check"),
        (CASH, "Cash"),
    )
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=TYPE_CHOICES, initial=CC,error_messages={'required': 'Please choose a payment method'})
    AMOUNT = "Amount"
    COMP = "Comp"
    NONE = "N"
    ELECTRICITY_CHOICES = (
        (AMOUNT, "$75"),
        (COMP, "Comp"),
        (NONE, "None"),
    )
    electricity_types = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices=ELECTRICITY_CHOICES, initial=AMOUNT,error_messages={'required': 'Please choose an electricity method'})
    email_list = forms.ModelChoiceField(error_messages={'required': 'Select an email list'},label='Email List',widget=forms.Select(attrs={'class':'form-control m-b'}),queryset=csvUpload.objects.all().order_by('created_at'), initial=None, empty_label='Please select a list', required=False)

class csvform(forms.ModelForm):
    class Meta:
        model = csvUpload
        fields = ['name','csv','is_visible']



class CreditCardDepositConfirmFormCoin(forms.Form):
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

class MediaKitForm(forms.ModelForm):
    class Meta:
        model = MediaKit
        fields = ['vendor_name',
                  'business_name',
                  'business_category',
                  'email',
                  'session',
                  'booth_offered',
                  'normal_price',
                  'one_show_price',
                  'two_show_price',
                  'three_show_price',
                  'prize_value',
                  'special_instructions_one',
                  'special_instructions_two',
                  'special_instructions_three',
                  'opening_remarks',
                  ]


class PromoCodeForm(forms.Form):
    code = forms.CharField(max_length=255, label='Code:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 123456'}),
                             error_messages={'required': 'Please Provide Proper Code',
                                             'invalid': 'Please Enter Valid Code'})

    amount_percent = forms.CharField(max_length=255, label='Amount:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 25'}),
                             error_messages={'required': 'Please Provide Amount',
                                             'invalid': 'Please Enter Amount'})
    PROMO_TYPE = (
        ('amount', 'Amount'),
        ('percent', 'Percentage'),
    )
    type = forms.ChoiceField(label='Discount Type:',
                             widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Discount Type'}),
                             choices=PROMO_TYPE)
    is_Available = forms.BooleanField(label='Ticket Available: ', required=False)


class EventTicketForm(forms.Form):
    name = forms.CharField(max_length=255, label='Name:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: Pleasanton DoubleTree - (12PM-4PM) '}),
                             error_messages={'required': 'Please Provide Proper Name',
                                             'invalid': 'Please Enter Valid Name'})

    standard_amount = forms.CharField(max_length=255, label='Standard Ticket Price:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 10.0'}),
                             error_messages={'required': False,
                                             'invalid': 'Please Enter Valid Standard Ticket Price'})

    early_bird_amount = forms.CharField(max_length=255, label='EarlyBird Ticket Price:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 10.0'}),
                             error_messages={'required': False,
                                             'invalid': 'Please Enter Valid EarlyBird Ticket Price'})

    group_amount = forms.CharField(max_length=255, label='Group Ticket Price:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 10.0'}),
                             error_messages={'required': False,
                                             'invalid': 'Please Enter Valid Group ticket Price'})

    event_date = forms.CharField(label='Event Date:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: YYYY-MM-DD'}),
                             error_messages={'required': 'Please Provide Event Date',
                                             'invalid': 'Please Enter Valid Event Date'})

    is_Expire = forms.BooleanField(label='Ticket Expire ', required=False)



class CreditCardBAWFTicketForm(forms.Form):
    # event = forms.ModelChoiceField(queryset=Event_fairs.objects.filter(date__gte=datetime.now().date()))
    email = forms.EmailField(max_length=255, label='Email:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
                             error_messages={'required': 'Please Provide Proper Email',
                                             'invalid': 'Please Enter Valid Email'})
    phone = forms.CharField(max_length=255, label='Phone:',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
                            error_messages={'required': 'Please Provide Proper Phone',
                                            'invalid': 'Please Enter Valid Phone'})
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
    number = forms.CharField(max_length=255, label='Card No:',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}),
                             error_messages={'required': 'Please Provide Proper Number without any dash/"-"',
                                             'invalid': 'Please Enter Card Number without Spaces and Dashes'})
    month = forms.ChoiceField(label='Expiry Month:',
                              widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Expiry Month'}),
                              choices=MONTH_CHOICES)
    year = forms.ChoiceField(label='Expiry Year:',
                             widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Expiry Year'}),
                             choices=YEAR_CHOICES)

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





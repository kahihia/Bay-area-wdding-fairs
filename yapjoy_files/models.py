from django.db import models
from yapjoy_events.models import HostEvent
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from yapjoy_registration.commons import id_generator
import stripe
from datetime import datetime
from datetime import datetime
class CSVFile(models.Model):
    csvfile = models.FileField(upload_to='media/')
    hostevent = models.ForeignKey(HostEvent, related_name='csvfile_to_event')

class WpInfo(models.Model):
    firstname = models.CharField(max_length=128, blank=True, null=True)
    lastname = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField(default=0)
    date = models.DateField(null=True, blank=True)
    accept = models.BooleanField(default=False)
    event = models.ForeignKey(HostEvent, related_name='wpinfo_to_event')

class CardChange(models.Model):
    email = models.CharField(max_length=500, null=True, blank=True)
    code = models.CharField(max_length=300, null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class UserInfo(models.Model):
    csvfile = models.ForeignKey(CSVFile, related_name='userinfo_files')

    LastName = models.CharField(max_length=255, blank=True, null=True)
    Email = models.CharField(max_length=255, blank=True, null=True)
    MailingStreet = models.CharField(max_length=255, blank=True, null=True)
    MailingCity = models.CharField(max_length=255, blank=True, null=True)
    OtherCity = models.CharField(max_length=255, blank=True, null=True)
    MailingState = models.CharField(max_length=255, blank=True, null=True)
    MailingZip = models.CharField(max_length=255, blank=True, null=True)

    BridesFirstName = models.CharField(max_length=255, blank=True, null=True)
    BridesLastName = models.CharField(max_length=255, blank=True, null=True)

    WeddingLocation = models.CharField(max_length=255, blank=True, null=True)
    Budget = models.CharField(max_length=255, blank=True, null=True)

    VendorInterestedIn = models.CharField(max_length=255, blank=True, null=True)
    WeddingDate = models.DateField(null=True, blank=True)
    userprofileID = models.IntegerField(default=0)

    # VENUE = 'Venues'
    # RING = "Jewelry"
    # BRIDE_DRESS = "Bridal Wear"
    # GROOM_SUIT = "Menswear"
    # FLORAL_DESIGN = "Florists"
    # HAIR = "Health & Beauty"
    # PHOTO = "Photo/Video"
    # CAKE = "Cake"
    # DJ = "DJ/Lighting"
    # Live_Music = "Live_Music"
    # Limo = "Limo"
    # WEDDING_PLANNER = "Planner"
    # INVITATION = "Invitation"
    # GIFT = "Favors & Decor"
    # OTHERS = "Catering"
    #
    # CATEGORY_OPTIONS = (
    #     (VENUE, "Venues & Event Spaces"),
    #     (RING, "Jewelry"),
    #     (BRIDE_DRESS, "Bride Dress"),
    #     (GROOM_SUIT, "Groom Suit"),
    #     (FLORAL_DESIGN, "Floral Design"),
    #     (HAIR, "Hair Make-Up"),
    #     (PHOTO, "Photo Video"),
    #     (CAKE, "Cake Bakers"),
    #     (DJ, "DJ Music"),
    #     (Limo, "Limo Travel"),
    #     (WEDDING_PLANNER, "Wedding Planner"),
    #     (INVITATION, "Inivtation"),
    #     (GIFT, "Gift"),
    #     (OTHERS, "Others"),
    # )
    # category = models.CharField(max_length=50, choices=CATEGORY_OPTIONS, default=VENUE)

    # csvFile_url = models.CharField(max_length=255, null=True, blank=True)
    # def get_file_url(self):
    #     return "%s%s"%(settings.MEDIA_URL, self.csvFile)

class Event_fairs(models.Model):
    name = models.CharField(max_length=1000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=1000, null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    amount = models.CharField(max_length=255, null=True, blank=True)
    earlybird_ticket = models.CharField(max_length=255, blank=True, null=True)
    group_ticket = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    google_location = models.CharField(max_length=255, null=True, blank=True)
    # season = models.CharField(max_length=20, null=True, blank=True)
    # is_soldout = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def check_date(self):
        # print self.date, datetime.today().date()
        if self.date < datetime.today().date():
            return False
        return True

    def __str__(self):
        return "%s - %s"%(self.name, self.date)

#For bg users only
class CategoryOptions(models.Model):
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
        (EVERYTHING, "EVERYTHING"),
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
    category = models.CharField(max_length=50, choices=CATEGORY_OPTIONS, default=EVERYTHING)
    def __str__(self):
        return self.category


class EventInvoiceDetail(models.Model):
    event_invoice = models.ForeignKey("EventInvoice")
    vendor_register = models.ForeignKey("InvoiceRegisterVendor")
    deposit = models.IntegerField(default=0, null=True, blank=True)
    balance1 = models.IntegerField(default=0, null=True, blank=True)
    balance2 = models.IntegerField(default=0, null=True, blank=True)
    balance3 = models.IntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_paid_amounts(self):
        amount = 0
        if self.check_deposit_paid() == "Paid":
            amount += self.deposit
        if self.check_balance1_paid() == "Paid":
            amount += self.balance1
        if self.check_balance2_paid() == "Paid":
            amount += self.balance2
        if self.check_balance3_paid() == "Paid":
            amount += self.balance3
        return amount

    def check_deposit_paid(self):
        if self.event_invoice.transaction_id_deposit:
            return "Paid"
        else:
            return "Not Paid"

    def check_balance1_paid(self):
        if self.event_invoice.transaction_id_balance1:
            return "Paid"
        else:
            return "Not Paid"

    def check_balance2_paid(self):
        if self.event_invoice.transaction_id_balance2:
            return "Paid"
        else:
            return "Not Paid"

    def check_balance3_paid(self):
        if self.event_invoice.transaction_id_balance3:
            return "Paid"
        else:
            return "Not Paid"

    def check_deposit(self):

        if self.deposit and EventInvoiceRequest.objects.filter(event_invoice_id=self.event_invoice.id,
                                                       type=EventInvoiceRequest.DEPOSIT).count() <= 0:
            return 'Pending'
        else:
            return 'Sent'

    def check_balance1(self):
        if self.balance1 and EventInvoiceRequest.objects.filter(event_invoice=self.event_invoice,
                                                       type=EventInvoiceRequest.BALANCE1).count()<=0:
            return 'Pending'
        else:
            return 'Sent'

    def check_balance2(self):
        if self.balance2 and EventInvoiceRequest.objects.filter(event_invoice=self.event_invoice,
                                                       type=EventInvoiceRequest.BALANCE2).count()<=0:
            return 'Pending'
        else:
            return 'Sent'

    def check_balance3(self):
        if self.balance3 and EventInvoiceRequest.objects.filter(event_invoice=self.event_invoice,
                                                       type=EventInvoiceRequest.BALANCE3).count()<=0:
            return 'Pending'
        else:
            return 'Sent'


class EventInvoice(models.Model):
    # event = models.ForeignKey("Register_Event")
    email = models.CharField(max_length=255, null=True, blank=True)
    deposit_date = models.DateField(null=True, blank=True)
    balance1_date = models.DateField(null=True, blank=True)
    balance2_date = models.DateField(null=True, blank=True)
    balance3_date = models.DateField(null=True, blank=True)

    transaction_id_deposit = models.CharField(max_length=255, null=True, blank=True)
    transaction_id_balance1 = models.CharField(max_length=255, null=True, blank=True)
    transaction_id_balance2 = models.CharField(max_length=255, null=True, blank=True)
    transaction_id_balance3 = models.CharField(max_length=255, null=True, blank=True)
    is_manual = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    transaction_id_deposit_date = models.DateTimeField(null=True, blank=True)
    transaction_id_balance1_date = models.DateTimeField(null=True, blank=True)
    transaction_id_balance2_date = models.DateTimeField(null=True, blank=True)
    transaction_id_balance3_date = models.DateTimeField(null=True, blank=True)

    invoices = models.ManyToManyField(EventInvoiceDetail)
    register_event = models.ForeignKey("Register_Event", null=True, blank=True)

    code = models.CharField(max_length=255, null=True, blank=True)
    def get_shows(self):
        shows = ""
        inv = self.invoices.all()
        for o in inv:
            if o.vendor_register.register.event.name:
                shows += o.vendor_register.register.event.name + " "
        return shows
    def get_deposited_amount(self):
        amount = 0
        inv = self.invoices.all()
        for o in inv:
            amount += o.deposit
        return amount


    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    def check_deposit_date_if_future(self):
        today = datetime.now().date()
        # print 'checking invoice future'
        # print self.deposit_date, today
        if self.deposit_date:
            if not self.deposit_date <= today:
                # print 'sending responase: ',"<span style='color: red;'><b>(Future) </b></span>"
                return mark_safe("<span style='color: red;'><b>(Future) </b></span>")
        else:
            return ""
    def get_transaction_id_deposit_date(self):
        if self.transaction_id_deposit:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            ch = stripe.Charge.retrieve(self.transaction_id_deposit)
            return convertTime(ch['created'])

    def get_transaction_id_balance1_date(self):
        if self.transaction_id_deposit:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            ch = stripe.Charge.retrieve(self.transaction_id_balance1)
            return convertTime(ch['created'])

    def get_transaction_id_balance2_date(self):
        if self.transaction_id_deposit:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            ch = stripe.Charge.retrieve(self.transaction_id_balance2)
            return convertTime(ch['created'])


    def get_transaction_id_balance3_date(self):
        if self.transaction_id_deposit:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            ch = stripe.Charge.retrieve(self.transaction_id_balance3)
            return convertTime(ch['created'])

    def __str__(self):
        return self.email

def convertTime(time):
    return datetime.fromtimestamp(
        int(time)
    ).strftime('%Y-%m-%d %H:%M:%S')

from yapjoy import settings
from datetime import datetime, timedelta
class EventInvoiceRequest(models.Model):
    event_invoice = models.ForeignKey("EventInvoice")
    code = models.CharField(max_length=255, null=True, blank=True)
    PENDING = "Pending"
    VIEWED = "Viewed"
    PAID = "Paid"
    SIGNED = "Signed"
    REJECTED = "Rejected"
    CANCEL = "Cancel"
    FAILED = "Failed"
    STATUS_CHOICES = {
        (PENDING, "Pending"),
        (VIEWED, "Viewed"),
        (PAID, "Paid"),
        (SIGNED, "Signed"),
        (REJECTED, "Rejected"),
        (FAILED, "Failed"),
        (CANCEL, "Cancel"),

    }
    DEPOSIT = "Deposit"
    BALANCE1 = "Balance1"
    BALANCE2 = "Balance2"
    BALANCE3 = "Balance3"
    TYPE_CHOICES = {
        (DEPOSIT, "Deposit"),
        (BALANCE1, "Balance1"),
        (BALANCE2, "Balance2"),
        (BALANCE3, "Balance3"),

    }
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    check_no = models.CharField(max_length=255, null=True, blank=True)
    signing_date = models.CharField(max_length=255, null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, related_name='cancelled_by_eir', null=True, blank=True)
    def check_expiry(self):
        two_days_ahead = self.created_at.date() + timedelta(days=3)
        print 'checking expiry: ',self.id,self.status, self.created_at.date(), two_days_ahead, datetime.now().date()
        if two_days_ahead < datetime.now().date():
            print 'returning true'
            return True
        print 'returning false'
        return False

    def get_deposit_date(self):
        if self.event_invoice.is_manual:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                date = datetime.fromtimestamp(
                        int(stripe.Charge.retrieve(self.transaction_id)['created'])
                    ).strftime('%Y-%m-%d %H:%M:%S')
                return "The agreement was signed digitally by %s with %s and Initial deposit was paid at %s"%(self.event_invoice.register_event.name, self.event_invoice.register_event.business_name,date)
            except:
                return "The agreement was signed digitally by %s with %s and Initial deposit was paid."%(self.event_invoice.register_event.name, self.event_invoice.register_event.business_name)
        else:
            return "This agreement is approved by %s with %s on %s, If you have any questions, please feel free to contact us at info@BayAreaWeddingFairs.com"%(self.event_invoice.register_event.name, self.event_invoice.register_event.business_name, self.event_invoice.deposit_date)
    agreement_code = models.CharField(max_length=255, null=True, blank=True)

    def get_agreement_code(self):
        try:
            return Register_Event_Aggrement.objects.get(id=self.agreement_code).code
        except Exception as e:
            print e
            return ""
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=DEPOSIT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_amount(self):
        total_amount = 0
        # print 'invoice id: ',self.event_invoice_id
        for o in self.event_invoice.invoices.all():
            if self.type == self.DEPOSIT and self.event_invoice.transaction_id_deposit:
                total_amount += o.deposit
            elif self.type == self.BALANCE1 and self.event_invoice.transaction_id_balance1:
                total_amount += o.balance1
            elif self.type == self.BALANCE2 and self.event_invoice.transaction_id_balance2:
                total_amount += o.balance2
            elif self.type == self.BALANCE3 and self.event_invoice.transaction_id_balance3:
                total_amount += o.balance3
        return total_amount

    def get_amount_sent(self):
        total_amount = 0
        for o in self.event_invoice.invoices.all():
            if self.type == self.DEPOSIT:
                total_amount += o.deposit
            elif self.type == self.BALANCE1:
                total_amount += o.balance1
            elif self.type == self.BALANCE2:
                total_amount += o.balance2
            elif self.type == self.BALANCE3:
                total_amount += o.balance3
        return total_amount

    def get_event(self):
        try:
            events = self.event_invoice.invoices.select_related('vendor_register','vendor_register__register','vendor_register__register__event').all()
            ret_str = ""
            for o in events:
                ret_str += "%s - %s<br />"%(o.vendor_register.register.event.name, str(o.vendor_register.register.event.date))
            return mark_safe(ret_str)
        except Exception as e:
            print e
            return "N/A"

    def get_event_b1(self):
        try:
            events = self.event_invoice.invoices.all()
            ret_str = ""
            for o in events:
                if o.balance1:
                    ret_str += "(%s - %s) "%(o.vendor_register.register.event.name, o.vendor_register.register.event.date)
            return ret_str
        except Exception as e:
            print e
            return "N/A"

    def get_event_b2(self):
        try:
            events = self.event_invoice.invoices.all()
            ret_str = ""
            for o in events:
                if o.balance2:
                    ret_str += "(%s - %s) " % (
                    o.vendor_register.register.event.name, o.vendor_register.register.event.date)
            return ret_str
        except Exception as e:
            print e
            return "N/A"

    def get_event_b3(self):
        try:
            events = self.event_invoice.invoices.all()
            ret_str = ""
            for o in events:
                if o.balance3:
                    ret_str += "(%s - %s) " % (
                    o.vendor_register.register.event.name, o.vendor_register.register.event.date)
            return ret_str
        except Exception as e:
            print e
            return "N/A"

class Register_Event_Interested(models.Model):
    event = models.ManyToManyField(Event_fairs, related_name="register_event_interested_event")
    user = models.ForeignKey(User, related_name="register_event_interested_user")
    name = models.CharField(max_length=500, null=True, blank=True)
    business_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    zip = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=500, null=True, blank=True)
    reference = models.CharField(max_length=500, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)


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
        (EVERYTHING, "EVERYTHING"),
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
        (OTHERS, "Other(Please mention below)"),
    )

    HEARD = ""
    GOOGLE = "Google"
    FACEBOOK = "Facebook"
    RADIO = "Radio"
    EMAIL = "Received Email"
    GUIDE = "Here comes the guide"
    THEKNOT = "TheKnot"
    FRIENDS_FAMILY = "Friends & Family"
    OTHER = "Other"

    HEARD_CHOICES = {
        (HEARD, "How did you hear about us?"),
        (GOOGLE, "Google"),
        (FACEBOOK, "Facebook"),
        (RADIO, "Radio"),
        (GUIDE, "Here comes the guide"),
        (THEKNOT, "TheKnot"),
        (FRIENDS_FAMILY, "Friends & Family"),
        (OTHER, "Other"),
    }

    PAID = "Paid"
    UNPAID = "Unpaid"
    REMOVED = "Deleted"
    STATUS_CHOICES = {
        (PAID, "Paid"),
        (UNPAID, "Unpaid"),
        (REMOVED, "Deleted"),

    }

    CASH = "Paid"
    CREDITCARD = "CreditCard"
    CHECK = "Check"
    WINNER = "Winner"
    COMP = "COMP"

    PAYMENT_METHOD = {
        (CASH, "Paid"),
        (CREDITCARD, "CreditCard"),
        (CHECK, "Check"),
        (WINNER, "Winner"),
        (COMP, "COMP"),

    }

    BGUSER = "BrideGroom"
    CONTRACTOR = "Vendor"
    UNKNOWNPROFILE = "Unknown"
    TYPE_CHOICES = (
        (BGUSER, "Bride/Groom"),
        (CONTRACTOR, "Vendor"),
        (UNKNOWNPROFILE, "Unknown"),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=UNKNOWNPROFILE)
    weddingDate = models.DateTimeField(null=True, blank=True)

    how_heard = models.CharField(max_length=50, choices=HEARD_CHOICES, help_text="Please select", null=True, blank=True)

    # for wp usrs only
    category = models.CharField(max_length=50, choices=CATEGORY_OPTIONS, help_text="Please select", null=True, blank=True)

    #for bg users only
    categories = models.ManyToManyField(CategoryOptions)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=UNPAID, null=True, blank=True)

    amount_due = models.IntegerField(default=0)
    commission = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default=CREDITCARD)
    description = models.CharField(max_length=5000, null=True, blank=True)
    sales = models.ForeignKey(User, related_name='interested_sales_officers', null=True, blank=True)
    is_lasVegasSignIn = models.BooleanField(default=False)


    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s"%(self.id, self.email)

class SalesCommission(models.Model):
    sales = models.ForeignKey(User)
    amount = models.FloatField(default=0)
    is_commission_paid = models.BooleanField(default=False)
    paid_by = models.ForeignKey(User, related_name="paid_by_salescommission")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)



class Register_Event(models.Model):
    event = models.ForeignKey(Event_fairs)
    user = models.ForeignKey(User, related_name='exhibitors')
    name = models.CharField(max_length=500, null=True, blank=True)
    business_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    zip = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=500, null=True, blank=True)
    grand_prize = models.CharField(max_length=500, null=True, blank=True)
    #qrcode = models.CharField(max_length=500, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

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
        (EVERYTHING, "EVERYTHING"),
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
        (OTHERS, "Other(Please mention below)"),
    )

    HEARD = ""
    GOOGLE = "Google"
    LINKEDIN = "Linkedin"
    FACEBOOK = "Facebook"
    RADIO = "Radio"
    EMAIL = "Received Email"
    GUIDE = "Here comes the guide"
    THEKNOT = "TheKnot"
    FRIENDS_FAMILY = "Friends & Family"
    OTHER = "Other"
    EVERYTHING_OP = "Everything"

    HEARD_CHOICES = {
        (HEARD, "How did you hear?"),
        (GOOGLE, "Google"),
        # (GOOGLE, "Google"),
        (LINKEDIN, "Linkedin"),
        (FACEBOOK, "Facebook"),
        (RADIO, "Radio"),
        (GUIDE, "Here comes the guide"),
        (THEKNOT, "TheKnot"),
        (FRIENDS_FAMILY, "Friends & Family"),
        (OTHER, "Other"),
        (EVERYTHING_OP, "Everything"),
    }

    PAID = "Paid"
    UNPAID = "Unpaid"
    REMOVED = "Deleted"
    STATUS_CHOICES = {
        (PAID, "Paid"),
        (REMOVED, "Deleted"),

    }

    SKINNYSTANDARD = "Skinny Std"
    STANDARD = "Tabletop (7x5)"
    DELUXE = "Deluxe (10x8)"
    PREMIUM = "Premium (15x8)"
    DOUBLEWIDE = "Doublewide"
    BOOTH_CHOICES = {
        (SKINNYSTANDARD, "Skinny Std"),
        (STANDARD, "Tabletop (7x5)"),
        (DELUXE, "Deluxe (10x8)"),
        (PREMIUM, "Premium (15x8)"),
        (DOUBLEWIDE, "Doublewide"),

    }
    FOOD = "Food"
    BAVERAGE = "Beverage"
    BOTH = "Food & Beverage"
    SNACKS_CHOICES = {
        (FOOD, "Food"),
        (BAVERAGE, "Beverage"),
        (BOTH, "Food & Beverage"),

    }

    CASH = "Paid"
    CREDITCARD = "CreditCard"
    CHECK = "Check"
    WINNER = "Winner"
    COMP = "COMP"

    PAYMENT_METHOD = {
        (CASH, "Paid"),
        (CREDITCARD, "CreditCard"),
        (CHECK, "Check"),
        (WINNER, "Winner"),
        (COMP, "COMP"),

    }

    BGUSER = "BrideGroom"
    CONTRACTOR = "Vendor"
    UNKNOWNPROFILE = "Unknown"
    TYPE_CHOICES = (
        (BGUSER, "Bride/Groom"),
        (CONTRACTOR, "Vendor"),
        (UNKNOWNPROFILE, "Unknown"),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=UNKNOWNPROFILE)
    weddingDate = models.DateTimeField(null=True, blank=True)


    how_heard = models.CharField(max_length=50, choices=HEARD_CHOICES, help_text="Please select", null=True, blank=True)

    #for wp usrs only
    category = models.CharField(max_length=50, choices=CATEGORY_OPTIONS, help_text="Please select", null=True, blank=True)

    #for bg users only
    categories = models.ManyToManyField(CategoryOptions, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=UNPAID, null=True, blank=True)
    booth = models.CharField(max_length=50, choices=BOOTH_CHOICES, null=True, blank=True)
    food = models.CharField(max_length=50, choices=SNACKS_CHOICES, null=True, blank=True)
    is_fashionshow = models.BooleanField(default=False)
    is_partner_vendor = models.BooleanField(default=False)
    backdrop_allowed = models.BooleanField(default=False)

    amount_due = models.IntegerField(default=0)
    have_invoices = models.IntegerField(default=0, null=True, blank=True)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    pay_unconditional = models.IntegerField(default=0, null=True, blank=True)
    commission = models.FloatField(default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default=CREDITCARD)
    description = models.CharField(max_length=5000, null=True, blank=True)
    sales = models.ForeignKey(User, related_name='sales_officers', null=True, blank=True)
    is_lasVegasSignIn = models.BooleanField(default=False)
    is_commission_paid = models.BooleanField(default=False)
    sales_commission = models.ForeignKey(SalesCommission, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # created_at.editable = True

    def __str__(self):
        return "%s - %s - %s (%s)"%(self.id, self.email, self.event.name, self.created_at.date())

    def record_amount_due(self):
        self.amount_due = self.get_amount_due()
        self.total_amount = self.get_amount_total()
        self.save()

    def get_percent_amount(self):
        if self.total_amount:
            total_amount = self.total_amount
            if self.commission:
                return (float(total_amount/100.00))*float(self.commission)
            else:
                return 0
        else:
            return 0

    def get_amount_due(self):
        try:
            event_invoices_details = InvoiceRegisterVendor.objects.filter(register_id=self.id)
            # # print "register events: ",event_invoices_details.count()
            amount = 0
            for events in event_invoices_details:
                # print "Totals: ",events.get_total()
                amount += events.get_total()
            # print "Amount total delivered: ",amount
            invoices_deduct = EventInvoiceDetail.objects.filter(vendor_register__register_id=self.id)
            # print "invoices deduct: ",invoices_deduct
            # print "Invoice Count: ", invoices_deduct.count()
            for o in invoices_deduct:
                # print o.id
                # invoice = EventInvoiceRequest.objects.filter(event_invoice=o.event_invoice, status=EventInvoiceRequest.PAID)
                # invoice = EventInvoiceDetail.objects.filter(vendor_register__register_id=self.id)
                # invoice = EventInvoiceRequest.objects.filter(event_invoice__register_event_id=self.id)
                # print invoice
                # if invoice:

                # for inv in o:
                # print "Subtracting: ",o.get_paid_amounts()
                # print "Subtracting From: ",amount
                amount -= o.get_paid_amounts()

            if self.pay_unconditional:
                return_amount = amount - self.pay_unconditional
                # print "Returning Conditional: ",return_amount
                return return_amount
            # print "Return Normal: ",amount
            return amount
        except Exception as e:
            print e
        return 0
    def get_amount_total(self):
        try:
            event_invoices_details = InvoiceRegisterVendor.objects.filter(register_id=self.id)
            # print "register events: ",event_invoices_details.count()
            amount = 0
            for events in event_invoices_details:
                amount += events.get_total()
            return amount
        except Exception as e:
            print e
        return 0

class Register_Event_Aggrement(models.Model):
    user = models.ForeignKey(User)
    invoices = models.ManyToManyField('InvoiceRegisterVendor')
    PENDING = "Pending"
    VIEWED = "Viewed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    AUTOPAID = "Paid through System"
    STATUS_CHOICES = {
        (PENDING, "Pending"),
        (VIEWED, "Viewed"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (AUTOPAID, "Paid through System"),

    }
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Notes(models.Model):
    exhibitor = models.ForeignKey(Register_Event)
    note_writer = models.ForeignKey(User)
    note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class NotesEx(models.Model):
    exhibitor = models.ForeignKey(Register_Event_Interested)
    note_writer = models.ForeignKey(User)
    note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class SalesTasks(models.Model):

    exhibitor = models.ForeignKey(Register_Event, null=True, blank=True)
    # exhibitor_reg = models.ForeignKey(Register_Event_Interested, null=True, blank=True)
    sales = models.ForeignKey(User)

    subject = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    INPROGRESS = "In-Progress"
    COMPLETE = "Completed"

    STATUS_CHOICES = {
        (INPROGRESS, "In-Progress"),
        (COMPLETE, "Completed"),
    }

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=INPROGRESS, null=True, blank=True)
    dueDate = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class SalesTasksEx(models.Model):

    exhibitor = models.ForeignKey(Register_Event_Interested, null=True, blank=True)
    # exhibitor_reg = models.ForeignKey(Register_Event_Interested, null=True, blank=True)
    sales = models.ForeignKey(User)

    subject = models.CharField(max_length=500, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    INPROGRESS = "In-Progress"
    COMPLETE = "Completed"

    STATUS_CHOICES = {
        (INPROGRESS, "In-Progress"),
        (COMPLETE, "Completed"),
    }

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=INPROGRESS, null=True, blank=True)
    dueDate = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Invoice_Event(models.Model):
    registered_event = models.ForeignKey(Register_Event)
    user = models.ForeignKey(User)
    amount = models.IntegerField(default=0)
    prize = models.IntegerField(default=0)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s - (%s, %s, $%s)"%(self.id, self.registered_event.email,self.registered_event.name, self.amount)

    PAID = "Paid"
    UNPAID = "Unpaid"
    STATUS_CHOICES = {
        (PAID, "Paid"),
        (UNPAID, "Unpaid"),

    }
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=UNPAID, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=500, null=True, blank=True)
    code = models.CharField(max_length=500, null=True, blank=True)
    sending_date = models.DateField(null=True, blank=True)
    is_signed = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class BulkInvoices(models.Model):
    invoice_event = models.ManyToManyField(Invoice_Event)
    invoice_event_vendor = models.ManyToManyField("InvoiceRegisterVendor")
    amount = models.IntegerField(default=0)

    PAID = "Paid"
    UNPAID = "Unpaid"
    STATUS_CHOICES = {
        (PAID, "Paid"),
        (UNPAID, "Unpaid"),

    }
    email = models.CharField(max_length=500,  null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=UNPAID, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    is_signed = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    code = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_amount(self):
        amount = 0
        for o in self.invoice_event_vendor.all():
            amount += o.deposit
        return amount


class csvUpload(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    csv = models.FileField(upload_to='static/', null=False, blank=False)
    is_visible = models.BooleanField(default=True)
    amount = models.IntegerField(default=150)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s"%(self.id, self.name)

class UserCSV(models.Model):
    user = models.ForeignKey(User)
    csv = models.ForeignKey(csvUpload)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

class csvData(models.Model):
    csv = models.ForeignKey(csvUpload)
    email = models.CharField(max_length=500, null=True, blank=True)
    first_name = models.CharField(max_length=500, null=True, blank=True)
    last_name = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    zip = models.CharField(max_length=500, null=True, blank=True)
    wedding_date = models.CharField(max_length=500, null=True, blank=True)
    id_user = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def check_user(self):
        try:
            if not self.id_user:
                user = User.objects.get(email__iexact=self.email)
                self.id_user = user.id
                self.save()
                return "<a class='btn vd_btn vd_bg-green' href='/profile/%s/'>Message</a>"%(user.id)
            elif self.id_user == "N/A":
                return "<a class='btn vd_btn vd_bg-green' disabled>Invite</a>"
            else:
                return "<a class='btn vd_btn vd_bg-green' href='/profile/%s/'>Message</a>"%(self.id_user)
        except Exception as e:
            print e
            self.id_user = "N/A"
            self.save()
            return "<a class='btn vd_btn vd_bg-green' disabled>Invite</a>"

from django.template.defaulttags import mark_safe
class InvoiceRegisterVendor(models.Model):
    register = models.ForeignKey(Register_Event)

    list_price = models.IntegerField(default=0)
    offered_price = models.IntegerField(default=0)
    pv_prize_offered = models.CharField(max_length=500, null=True, blank=True)
    # deposit = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    # balance1 = models.IntegerField(default=0)
    # is_sent_balance1 = models.BooleanField(default=False)
    # balance2 = models.IntegerField(default=0)
    # is_sent_balance2 = models.BooleanField(default=False)
    # balance3 = models.IntegerField(default=0)
    # is_sent_balance3 = models.BooleanField(default=False)
    # date_deposit = models.DateField()
    # date_balance1 = models.DateField()
    # date_balance2 = models.DateField()
    # date_balance3 = models.DateField()
    # deposit_code = models.CharField(max_length=255, null=True, blank=True)
    # balance1_code = models.CharField(max_length=255, null=True, blank=True)
    # balance2_code = models.CharField(max_length=255, null=True, blank=True)
    # balance3_code = models.CharField(max_length=255, null=True, blank=True)
    email_list = models.ForeignKey(csvUpload, null=True, blank=True)

    CC = "CreditCard"
    CHECK = "Check"
    CASH = "Cash"
    TYPE_CHOICES = (
        (CC, "Credit Card"),
        (CHECK, "Check"),
        (CASH, "cash"),
    )
    payment_method = models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True)
    AMOUNT = "Amount"
    COMP = "Comp"
    NONE = "N"
    ELECTRICITY_CHOICES = (
        (AMOUNT, "$75"),
        (COMP, "Comp"),
        (NONE, "None"),
    )
    electricity_types = models.CharField(choices=ELECTRICITY_CHOICES, max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s"%(self.id, self.register.email)

    def get_status(self):
        amount = self.register.amount_due
        if amount:
            if amount <= 0:
                return mark_safe('<span>Paid</span>')
            else:
                return mark_safe('<span style="color: red;">Unpaid</span>')
        # print 'amount due: ',amount
        return mark_safe('<span>Paid</span>')

    def get_total(self):
        elec = 0
        lp = 0
        if self.electricity_types == self.AMOUNT:
            elec = 75
        if self.list_price:
            lp = self.list_price
        total = lp + int(self.offered_price) + elec
        return total

    def check_invoice_status_paid(self):
        eid = EventInvoiceDetail.objects.get(vendor_register_id=self.id)
        ei = eid.event_invoice
        paid = 0
        unpaid = 0
        list_payment = [InvoiceRegisterVendor.CC]
        if self.payment_method in list_payment:
            print 'inside cc, ',self.id
            if ei.deposit_date and eid.deposit:
                unpaid += 1
                if ei.transaction_id_deposit:
                    paid += 1
            if ei.balance1_date and eid.balance1:
                unpaid += 1
                if ei.transaction_id_balance1:
                    paid += 1
            if ei.balance2_date and eid.balance2:
                unpaid += 1
                if ei.transaction_id_balance2:
                    paid += 1
            if ei.balance3_date and eid.balance3:
                unpaid += 1
                if ei.transaction_id_balance3:
                    paid += 1
            print paid, unpaid
            if paid == unpaid:
                return "Paid"
            elif paid < unpaid:
                return "Unpaid"
            else:
                return "N/A"
        else:
            print 'inside check, ', self.id
            print ei.deposit_date, ei.id
            print ei.transaction_id_deposit
            if ei.deposit_date:
                unpaid += 1
                if ei.transaction_id_deposit:
                    paid += 1
            if ei.balance1_date:
                unpaid += 1
                if ei.transaction_id_balance1:
                    paid += 1
            if ei.balance2_date:
                unpaid += 1
                if ei.transaction_id_balance2:
                    paid += 1
            if ei.balance3_date:
                unpaid += 1
                if ei.transaction_id_balance3:
                    paid += 1
            print paid, unpaid
            if paid == unpaid:
                return "Paid"
            elif paid < unpaid:
                return "Unpaid"
            else:
                return "N/A"

class MediaKit(models.Model):
    user = models.ForeignKey(User)
    vendor_name = models.CharField(max_length=500, null=True, blank=True)
    business_name = models.CharField(max_length=500, null=True, blank=True)
    business_category = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(max_length=500, null=True, blank=True)
    WF2016 = "2016 Wedding Fairs"
    WF2017 = "2017 Wedding Fairs"
    WF2018 = "2018 Wedding Fairs"
    SESSION_CHOICES = (
        (WF2016, "2016 Wedding Fairs"),
        (WF2017, "2017 Wedding Fairs"),
        (WF2018, "2018 Wedding Fairs"),
    )
    STANDARD = "Standard"
    DELUXE = "Deluxe"
    DOUBLEWIDE = "Doublewide"
    SKINNYHIGHBOY = "Skinny-HighBoy"
    session = models.CharField(choices=SESSION_CHOICES, max_length=100, null=True, blank=True)
    BOOTH_CHOICES = (
        (STANDARD, "Standard"),
        (DELUXE, "Deluxe"),
        (DOUBLEWIDE, "Doublewide"),
        (SKINNYHIGHBOY, "Skinny-HighBoy"),
    )
    booth_offered = models.CharField(choices=BOOTH_CHOICES, max_length=100, null=True, blank=True)
    normal_price = models.CharField(max_length=50, null=True, blank=True)
    one_show_price = models.CharField(max_length=50, null=True, blank=True)
    two_show_price = models.CharField(max_length=50, null=True, blank=True)
    three_show_price = models.CharField(max_length=50, null=True, blank=True)
    prize_value = models.CharField(max_length=50, null=True, blank=True)
    special_instructions_one = models.CharField(max_length=1000, null=True, blank=True)
    special_instructions_two = models.CharField(max_length=1000, null=True, blank=True)
    special_instructions_three = models.CharField(max_length=1000, null=True, blank=True)
    opening_remarks = models.CharField(max_length=1000, null=True, blank=True)
    PENDING = 'Pending'
    VIEWED = 'Viewed'
    STATUS_CHOICES = {
        (PENDING, "Pending"),
        (VIEWED, "Viewed"),

    }
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING, null=True, blank=True)
    viewed = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

def media_kit_signal_view(sender, instance, created, **kwargs):
    if created:
        instance.code = id_generator(size=50)
        instance.save()
post_save.connect(media_kit_signal_view, sender=MediaKit)

def CardChange_signal_view(sender, instance, created, **kwargs):
    if created:
        instance.code = id_generator(size=50)
        instance.save()
post_save.connect(CardChange_signal_view, sender=CardChange)
from django.db import models
from django.db.models.signals import post_save, pre_save
from yapjoy_files import models as event

# Create your models here.
import string
import random



class EventTickets(models.Model):
    event = models.ForeignKey('yapjoy_files.Event_fairs', null=True, blank=True, related_name='event_fair', )
    phone = models.CharField(max_length=255, blank=True, null=True)
    card = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255)
    expire = models.CharField(max_length=255, null=True, blank=True)
    promocode_success = models.CharField(max_length=255, null=True, blank=True)
    amount = models.CharField(max_length=255, blank=True, null=True)
    earlybird_ticket = models.CharField(max_length=255, blank=True, null=True)
    group_ticket = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.CharField(max_length=255, blank=True, null=True)
    is_attended = models.BooleanField(default=False)
    code = models.CharField(max_length=255, null=True, blank=True)
    path_upload = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)


    def get_all_tickets(self):
        quan = 0
        quan_gr = 0
        quan_eb = 0
        if self.quantity:
            quan = int(self.quantity)
        if self.earlybird_ticket:
            quan_eb = int(self.earlybird_ticket)
        if self.group_ticket:
            quan_gr = int(self.group_ticket)
        return quan+quan_gr+quan_eb

    def __str__(self):
        return self.email

    def get_amount(self):
        if self.amount:
            amount = self.amount/100
            return amount


class Promocode(models.Model):
    code = models.CharField(max_length=255, blank=True, null=True)
    amount_percent = models.CharField(max_length=255, blank=True, null=True)
    PERCENT = "percent"
    AMOUNT = "amount"
    PROMO_TYPE = (
        (AMOUNT,'Amount'),
        (PERCENT,'Percentage'),
    )
    type = models.CharField(max_length=100, choices=PROMO_TYPE)
    is_Available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.code


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


from bayareaweddingfairs_tickets.views import send_email_bawf
def event_ticket_bought(sender, instance, created, **kwargs):
    if created:
        print "event created: ", created
        # send_email_bawf('mbysf@gmail.com',"Ticket is bought", 'mbysf@gmail.com', instance.email+" bought a ticket of "+instance.event)
        print "email send"
post_save.connect(event_ticket_bought, sender=EventTickets)
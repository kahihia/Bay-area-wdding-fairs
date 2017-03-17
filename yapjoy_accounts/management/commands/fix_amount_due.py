__author__ = 'adeel'


from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_registration.models import UserProfile, optionsSearch
from yapjoy_market.models import Product
from django.contrib.auth.models import User
from django.db.models import Q
from yapjoy_files.models import *
class Command(NoArgsCommand):
    help = 'Fix amount due'

    def handle_noargs(self, **options):
        counter = 0
        events = Register_Event.objects.all()
        for event in events:
            counter += 1
            amount_due = event.get_amount_due()
            if amount_due <= 0:
                amount_due = 0
            event.amount_due = amount_due
            event.total_amount = event.get_amount_total()
            event.save()
            print counter, event.email
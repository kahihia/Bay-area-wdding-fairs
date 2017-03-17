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
    help = 'Fix have invoices'

    def handle_noargs(self, **options):
        counter = 0
        events = Register_Event.objects.all()
        for event in events:
            if event.booth == "Standard (7x5)":
                event.booth = "Tabletop (7x5)"
            # elif event.booth == "Deluxe":
            #     event.booth = "Deluxe (10x8)"
            # elif event.booth == "Premium":
            #     event.booth = "Premium (15x8)"
            event.save()
            print event.id, event.email
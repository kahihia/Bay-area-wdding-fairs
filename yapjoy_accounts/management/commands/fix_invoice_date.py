__author__ = 'adeel'


from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_registration.models import UserProfile, optionsSearch
from yapjoy_market.models import Product
from django.contrib.auth.models import User
from django.db.models import Q
import stripe
from yapjoy_files.models import *
class Command(NoArgsCommand):
    help = 'Fix invoice date'

    def handle_noargs(self, **options):
        counter = 0
        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
        invoices = EventInvoice.objects.all()
        for invoice in invoices:
            if invoice.transaction_id_deposit and 'ch_' in invoice.transaction_id_deposit:
                print invoice.transaction_id_deposit
                date_dep = invoice.get_transaction_id_deposit_date()
                print date_dep
                invoice.transaction_id_deposit_date = date_dep
                invoice.save()
            if invoice.transaction_id_balance1 and 'ch_' in invoice.transaction_id_balance1:
                print invoice.transaction_id_balance1
                date_bal1 = invoice.get_transaction_id_balance1_date()
                print date_bal1
                invoice.transaction_id_balance1_date = date_bal1
                invoice.save()
            if invoice.transaction_id_balance2 and 'ch_' in invoice.transaction_id_balance2:
                print invoice.transaction_id_balance2
                date_bal2 = invoice.get_transaction_id_balance2_date()
                print date_bal2
                invoice.transaction_id_balance2_date = date_bal2
                invoice.save()
            if invoice.transaction_id_balance3 and 'ch_' in invoice.transaction_id_balance3:
                print invoice.transaction_id_balance3
                date_bal3 = invoice.get_transaction_id_balance3_date()
                print date_bal3
                invoice.transaction_id_balance3_date = date_bal3
                invoice.save()
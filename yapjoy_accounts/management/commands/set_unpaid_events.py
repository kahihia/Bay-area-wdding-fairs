__author__ = 'adeel'

from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_registration.models import UserProfile
from yapjoy_market.models import Product
from django.contrib.auth.models import User
from datetime import datetime
from yapjoy_files.models import *
class Command(NoArgsCommand):
    help = 'read and import csv for events'

    def handle_noargs(self, **options):
        print "read and import csv for events"
        with open('csv/Wedding_Fairs_C_001.csv', 'rU') as f:
            print "script started"
            reader = csv.reader(f)
            next(reader, None)
            mylist = []
            count = 0
            ln = 0
            bl = 0
            for row in reader:

                if row[13]:
                    date = datetime.strptime(row[13], "%m/%d/%y").date()
                    print row[13], date, row[1]
                    try:
                        events = Event_fairs.objects.get(date=date)
                        print "Event Exist"
                    except:
                        events = Event_fairs.objects.create(date=date, name=row[1])
                    if date < datetime.today().date():
                        events.is_expired = True
                        events.save()

                    with open('csv/Contracted_Vendors_as_of_May_10_2016.csv', 'rU') as fe:
                        print "script started"
                        reader2 = csv.reader(fe)
                        next(reader2, None)
                        counter = 0
                        for row2 in reader2:
                            if row[0] == row2[15] and row2[2]:
                                counter+=1
                                count+=1
                                user = None
                                try:
                                    user = User.objects.get(email__iexact=str(row2[2]).strip())
                                except:
                                    pass
                                    # user = User.objects.create(email=str(row2[2]).strip(),username=str(row2[2]).strip())
                                reg_eve = Register_Event.objects.filter(event=events,
                                                              user=user,
                                                              name="%s %s"%(row2[17],row2[19]),
                                                              business_name=row2[0],
                                                              phone=row2[1],
                                                              email=user.email,
                                                              comments=row2[12],
                                                              type=Register_Event.CONTRACTOR,
                                                              amount_due=int(float(row2[16])),
                                                              )
                                # date_created = datetime.strptime(str(row2[5]).split()[0], "%m/%d/%y").date()
                                # reg_eve.created_at =date_created
                                for o in reg_eve:
                                    o.pay_unconditional =o.amount_due
                                    o.save()
                                # InvoiceRegisterVendor.objects.create(register=reg_eve,
                                #                                            list_price=0,
                                #                                            offered_price=int(float(row2[16])),
                                #                                            pv_prize_offered=0,
                                #                                            # deposit=deposit,
                                #                                            # is_sent_deposit=send_email_now,
                                #                                            # balance1=balance1,
                                #                                            # balance2=balance2,
                                #                                            # balance3=balance3,
                                #                                            # date_balance1=date_balance1,
                                #                                            # date_balance2=date_balance2,
                                #                                            # date_balance3=date_balance3,
                                #                                            # date_deposit=date_deposit,
                                #                                            payment_method=row2[18],
                                #                                            electricity_types=0,
                                #                                            # email_list=0,
                                #                                            )
                        mylist.append({'name':events.name,'count':counter})
            print mylist
            print count
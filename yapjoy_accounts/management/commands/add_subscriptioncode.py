from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from django.contrib.auth.models import User
from yapjoy_registration.models import *
class Command(NoArgsCommand):
    help = 'read and import csv for BG subscription code'

    def handle_noargs(self, **options):
        print "read and import csv for BG subscription code"
        with open('B_G_List.csv', 'rU') as f:
            print "script started"
            reader = csv.reader(f)
            next(reader, None)
            mylist = []
            count = 0
            error_count = 0
            ln = 0
            bl = 0
            for row in reader:
                if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[1]):
                    try:
                        user = User.objects.get(email=row[1])
                        subcode = SubscriptionCode.objects.get_or_create(user=user)
                        print 'done'
                        count += 1
                        print count
                        # print row[7], row[0]
                    except Exception as e:
                        # pass
                        print e
                        error_count += 1
                        # print row[1]
                    # if row[0]:
                    #     ln += 1
                    # if row[8]:
                    #     bl += 1
                    # print row[0], row[8], row[10]
                    # count += 1
            print count, ln, bl, error_count
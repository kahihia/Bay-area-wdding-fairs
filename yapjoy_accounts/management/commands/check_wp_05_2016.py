from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from django.contrib.auth.models import User
from yapjoy_registration.models import optionsSearch, optionsSearch_users, Company, UserProfile
class Command(NoArgsCommand):
    help = 'read and import csv for wedding professionals'

    def handle_noargs(self, **options):
        print "read and import csv for wedding professionals"
        with open('Vendors_051016.csv', 'rU') as f:
            print "script started"
            reader = csv.reader(f)
            next(reader, None)
            mylist = []
            count = 0
            found = 0
            not_found = 0
            ln = 0
            bl = 0
            options = optionsSearch.objects.all()
            for row in reader:
                if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[3]):
                    count += 1
                    try:
                        user = None
                        try:
                            user = User.objects.get(email__iexact=row[3], username__iexact=row[3])
                            found += 1
                        except:
                            not_found += 1
                    except Exception as e:
                        # pass
                        print e
                        # error_count += 1
                        # print row[1]
                    # if row[0]:
                    #     ln += 1
                    # if row[8]:
                    #     bl += 1
                    # print row[0], row[8], row[10]
                    # count += 1
                    print count
            print "Total Existing: ",found
            print "New Users: ",not_found
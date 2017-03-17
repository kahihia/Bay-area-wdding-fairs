from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from django.contrib.auth.models import User
class Command(NoArgsCommand):
    help = 'read and import csv for brige and groom'

    def handle_noargs(self, **options):
        print "read and import csv for brige and groom"
        with open('B_G_List.csv', 'rU') as f:
            print "script started"
            reader = csv.reader(f)
            next(reader, None)
            mylist = []
            count = 0
            ln = 0
            bl = 0
            for row in reader:
                if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[1]):
                    if User.objects.filter(email__iexact=row[1]).count() == 0:
                        user = User.objects.create(username=row[1], email=row[1])
                        count += 1
                        print user.email, count
                        # profile = user.userprofile
                        # profile
                    # if row[0]:
                    #     ln += 1
                    # if row[8]:
                    #     bl += 1
                    # print row[0], row[8], row[10]
                    # count += 1
            print count, ln, bl
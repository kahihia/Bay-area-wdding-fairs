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
                    try:
                        user = User.objects.get(email__iexact=row[1])
                        user.first_name = row[7]
                        user.last_name = row[0]
                        user.save()
                        count += 1
                        # print row[7], row[0]
                    except Exception as e:
                        print e
                        print row[1]
                    # if row[0]:
                    #     ln += 1
                    # if row[8]:
                    #     bl += 1
                    # print row[0], row[8], row[10]
                    # count += 1
            print count, ln, bl
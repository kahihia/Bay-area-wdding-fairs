from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from django.contrib.auth.models import User
from yapjoy_registration.models import optionsSearch, optionsSearch_users
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
            error_count = 0
            ln = 0
            bl = 0
            options = optionsSearch.objects.all()
            for row in reader:
                if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[1]):
                    try:
                        user = User.objects.get(email__iexact=row[1])
                        profile = user.userprofile
                        # profile.street = row[2]
                        # profile.city = row[3]
                        # profile.state = row[5]
                        # profile.save()
                        # user.first_name = row[7]
                        # user.last_name = row[0]
                        # user.save()
                        for option in options:
                            if option.name in row[11]:
                                optionsSearch_users.objects.get_or_create(open_search=option, userprofile=profile)
                        # print row[11]#, row[3], row[5], 'Done'
                        count += 1
                        # print 'done'
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
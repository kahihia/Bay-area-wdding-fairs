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
        with open('WP2016.csv', 'rU') as f:
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
                            user = User.objects.create(email=row[3], username=row[3])
                            profile = UserProfile.objects.get(user=user)
                            user.first_name = row[1]
                            user.last_name = row[2]
                            user.save()
                            profile.phone = row[4]
                            profile.street = row[5]
                            profile.city = row[6]
                            profile.state = row[7]
                            profile.zip = row[8]
                            for option in options:
                                if option.name in row[9]:
                                    optionsSearch_users.objects.get_or_create(open_search=option, userprofile=profile)
                            company = Company.objects.create(userprofile=profile, name=row[0])
                            not_found += 1
                            print 'added'
                        # user.first_name = row[1]
                        # user.last_name = row[2]
                        # user.save()
                        # profile = user.userprofile
                        # company = Company.objects.get_or_create(userprofile=profile)[0]
                        # company.name = row[0]
                        # company.save()
                        # profile.phone = row[4]
                        # profile.street = row[5]
                        # profile.city = row[6]
                        # profile.state = row[7]
                        # profile.zip = row[8]
                        # profile.type = UserProfile.PROFESSIONAL
                        # profile.save()
                        # # profile.street = row[2]
                        # # profile.city = row[3]
                        # # profile.state = row[5]
                        # # profile.save()
                        # # user.first_name = row[7]
                        # # user.last_name = row[0]
                        # # user.save()
                        # for option in options:
                        #     if option.name in row[9]:
                        #         optionsSearch_users.objects.get_or_create(open_search=option, userprofile=profile)
                        # # print row[11]#, row[3], row[5], 'Done'
                        # count += 1
                        # print 'done: ',count
                        # print 'done'
                        # print row[7], row[0]
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
                print count, found, not_found
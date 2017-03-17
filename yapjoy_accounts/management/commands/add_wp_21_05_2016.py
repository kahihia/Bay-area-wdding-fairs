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
                            #print 'Found: ', user
                        except Exception as e:
                            print "Exception inside 1st: ",e
                            print row
                            print "Adding the user"
                            user = User.objects.create(email=row[3], username=row[3])
                            print 'user is added'
                            profile = UserProfile.objects.get(user=user)
                            print 'getting profile'
                            user.first_name = row[1]

                            print 'adding name'
                            user.last_name = row[2]
                            print 'adding second name'
                            user.save()
                            profile.phone = row[4]
                            profile.save()
                            print 'adding profile and save'
                            # if row[5]:
                            Company.objects.create(userprofile=profile, name=row[5])
                            print 'adding company'
                            for option in options:
                                if option.name in row[5]:
                                    optionsSearch_users.objects.get_or_create(open_search=option, userprofile=profile)
                            print 'added options'
                            not_found += 1
                            print 'Added: ',user
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
                        print "Exception inside 2nd: ",e
                        # error_count += 1
                        # print row[1]
                    # if row[0]:
                    #     ln += 1
                    # if row[8]:
                    #     bl += 1
                    # print row[0], row[8], row[10]
                    # count += 1
            print count, found, not_found
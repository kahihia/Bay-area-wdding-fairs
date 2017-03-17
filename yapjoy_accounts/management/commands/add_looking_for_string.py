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
        count = 0
        for user in User.objects.all().order_by('username'):
            try:
                profile = user.userprofile
                looking_for_string = ""
                ops = optionsSearch_users.objects.select_related('open_search').filter(userprofile=profile)
                if ops:
                    for op in ops:
                        looking_for_string += "%s "%(op.open_search.name)
                    profile.looking_for = looking_for_string
                    profile.save()
                count += 1
                print count, user.email, looking_for_string
            except Exception as e:
                print e

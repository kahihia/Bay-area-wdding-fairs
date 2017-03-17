__author__ = 'adeel'
#
# if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
#                     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
#                     Product.objects.create(title='Videography',user=user,status=Product.PENDING)

from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_registration.models import UserProfile
from yapjoy_market.models import Product
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
                        profile = user.userprofile
                        if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
                            Product.objects.get_or_create(title='Bridal Attire',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Beauty',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Bridal Registry',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Caterers',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Flowers',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Equipment Rental',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Favors',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Honeymoon',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Invitations',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Transportation',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Photography',user=user,status=Product.PENDING)
                            Product.objects.get_or_create(title='Videography',user=user,status=Product.PENDING)
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
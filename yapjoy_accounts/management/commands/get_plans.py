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
from yapjoy_registration.models import UserProfile, optionsSearch
from yapjoy_market.models import Product
from django.contrib.auth.models import User
from django.db.models import Q
class Command(NoArgsCommand):
    help = 'read and import csv for brige and groom'

    def handle_noargs(self, **options):
        user_list = []
        users = User.objects.all()
        count = users.count()
        try:
            for user in users:
                count -= 1
                try:
                    pr = Product.objects.filter(user=user).count()
                    if pr > 0:
                        user_list.append({'email':user.email,'products':pr})
                        print user.email, pr
                except Exception as e:
                    print e
                # print count
            user_list.sort()
            # print user_list
            for o in user_list:
                print o['email'], o['products']
            # print row[7], row[0]
        except Exception as e:
            print e
        # if row[0]:
        #     ln += 1
        # if row[8]:
        #     bl += 1
        # print row[0], row[8], row[10]
        # count += 1
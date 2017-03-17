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
        print "read and import csv for brige and groom"
        count = 0
        everything = optionsSearch.objects.get(name="Everything")
        favorsAndDecor = optionsSearch.objects.get(name="Favors and Decor")
        invitation = optionsSearch.objects.get(name="Invitation")
        liveMusic = optionsSearch.objects.get(name="Live Music")
        lighting = optionsSearch.objects.get(name="Lighting")
        dJ = optionsSearch.objects.get(name="DJ")
        planner = optionsSearch.objects.get(name="Planner")
        healthAndBeauty = optionsSearch.objects.get(name="Health and Beauty")
        cake = optionsSearch.objects.get(name="Cake")
        florist = optionsSearch.objects.get(name="Florist")
        limo = optionsSearch.objects.get(name="Limo")
        video = optionsSearch.objects.get(name="Video")
        photo = optionsSearch.objects.get(name="Photo")
        mensWear = optionsSearch.objects.get(name="Menswear")
        bridalWear = optionsSearch.objects.get(name="Bridal Wear")
        venues = optionsSearch.objects.get(name="Venues")
        catering = optionsSearch.objects.get(name="Catering")
        profiles = UserProfile.objects.select_related('user').filter(Q(type=UserProfile.BRIDE)|Q(type=UserProfile.GROOM)|Q(type=UserProfile.UNKNOWNPROFILE))
        print "Total count is: ", profiles.count()
        count = profiles.count()
        try:
            for profile in profiles:
                try:
                    user = profile.user
                    if Product.objects.filter(user=user,status=Product.PENDING).count() > 14:
                        Product.objects.filter(user=user,status=Product.PENDING).delete()
                        Product.objects.create(category=bridalWear,title='Bridal Attire',user=user,status=Product.PENDING)
                        Product.objects.create(category=healthAndBeauty,title='Beauty',user=user,status=Product.PENDING)
                        Product.objects.create(category=invitation,title='Bridal Registry',user=user,status=Product.PENDING)
                        Product.objects.create(category=catering,title='Caterers',user=user,status=Product.PENDING)
                        Product.objects.create(category=florist,title='Flowers',user=user,status=Product.PENDING)
                        Product.objects.create(category=planner,title='DJ',user=user,status=Product.PENDING)
                        Product.objects.create(category=planner,title='Equipment Rental',user=user,status=Product.PENDING)
                        Product.objects.create(category=catering,title='Rehearsal Dinner',user=user,status=Product.PENDING)
                        Product.objects.create(category=planner,title='Favors',user=user,status=Product.PENDING)
                        Product.objects.create(category=planner,title='Honeymoon',user=user,status=Product.PENDING)
                        Product.objects.create(category=invitation,title='Invitations',user=user,status=Product.PENDING)
                        Product.objects.create(category=limo,title='Transportation',user=user,status=Product.PENDING)
                        Product.objects.create(category=photo,title='Photography',user=user,status=Product.PENDING)
                        Product.objects.create(category=video,title='Videography',user=user,status=Product.PENDING)
                        count -= 1
                        print count, user.email
                    else:
                        count -= 1
                        print count
                except Exception as e:
                    print e
                    count -= 1
            # print row[7], row[0]
        except Exception as e:
            print e
        # if row[0]:
        #     ln += 1
        # if row[8]:
        #     bl += 1
        # print row[0], row[8], row[10]
        # count += 1
        print count
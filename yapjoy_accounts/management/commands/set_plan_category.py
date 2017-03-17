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
from yapjoy_market.models import Product, optionsSearch
from django.contrib.auth.models import User
class Command(NoArgsCommand):
    help = 'Fixing the plan missing category'

    def handle_noargs(self, **options):
        print "Setting category for plans"
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
        count = Product.objects.all().count()
        for product in Product.objects.all():
            if product.title == "Bridal Attire":
                product.category = bridalWear
            elif product.title == "Beauty":
                product.category = healthAndBeauty
            elif product.title == "Bridal Registry":
                product.category = invitation
            elif product.title == "Caterers":
                product.category = catering
            elif product.title == "Flowers":
                product.category = florist
            elif product.title == "Equipment Rental":
                product.category = planner
            elif product.title == "Rehearsal Dinner":
                product.category = catering
            elif product.title == "Favors":
                product.category = planner
            elif product.title == "Honeymoon":
                product.category = planner
            elif product.title == "Invitations":
                product.category = invitation
            elif product.title == "Transportation":
                product.category = limo
            elif product.title == "Photography":
                product.category = photo
            elif product.title == "Videography":
                product.category = video
            product.save()
            print count
            count -= 1

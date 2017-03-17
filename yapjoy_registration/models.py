from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from datetime import datetime
from .commons import id_generator
from yapjoy import settings
from yapjoy_yelpclient.client import *

def get_upload_dish_image_url_s3_file_name(instance, filename):
    now = datetime.now()

    file_name = str(filename.split('.')[-2]) + '_'+ str(now.year) + '_'+ str(now.month) + '_'+ str(now.second) + '.' + str(filename.split('.')[-1])

    return "media/videos/%s" % (file_name)
class UserProfile(models.Model):
    GROOM = "Groom"
    BRIDE = "Bride"
    PROFESSIONAL = "Professional"
    OTHER = "Other"
    EVENTMANAGER = "Event"
    UNKNOWNPROFILE = "Unknown"




    TYPE_CHOICES = (
        (OTHER, "Other"),
        (GROOM, "Groom"),
        (BRIDE, "Bride"),
        (PROFESSIONAL, "Wedding Professional (Vendor)"),
        (EVENTMANAGER, "Event Manager"),
        (UNKNOWNPROFILE, "Unknown Profile"),
    )

    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "N/A"


    GENDER_CHOICES = (
        (MALE, "Male"),
        (FEMALE, "Female"),
        (UNKNOWN, "N/A"),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=UNKNOWN)

    AGE_OPTION_NONE = 'Select'
    AGE_OPTION_ONE = '18-25'
    AGE_OPTION_TWO = '25-30'
    AGE_OPTION_THREE = '30+'

    AGE_OPTIONS = (
        (AGE_OPTION_NONE, "Select Age"),
        (AGE_OPTION_ONE, "18-25"),
        (AGE_OPTION_TWO, "25-30"),
        (AGE_OPTION_THREE, "30+"),
    )
    age = models.CharField(max_length=50, choices=AGE_OPTIONS, default=AGE_OPTION_NONE)

    wedding_date = models.DateField(null=True, blank=True)

    # profile_image = models.ImageField()
    # cover_image = models.ImageField()

    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=255, blank=True, null=True)
    is_review_request = models.BooleanField(default=False)
    review_request_date = models.CharField(max_length=500, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    user = models.OneToOneField(User)

    DEFAULT_IMAGE = 'media/tempPhoto.png'
    image = models.ImageField(upload_to='media/', null=True, blank=True, default=DEFAULT_IMAGE)
    DEFAULT_COVER_IMAGE = 'media/tempCanvas.png'
    cover_image = models.ImageField(upload_to='media/', null=True, blank=True, default=DEFAULT_COVER_IMAGE)
    date_of_birth = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=UNKNOWNPROFILE)
    video = models.FileField(upload_to=get_upload_dish_image_url_s3_file_name, default='', null=True, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    profession = models.CharField(max_length=255, blank=True)

    stripe_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_id_bawf = models.CharField(max_length=255, blank=True, null=True)
    activation_id = models.CharField(max_length=255, blank=True, null=True)
    dashboard_link = models.CharField(max_length=500, blank=True, null=True)
    amount = models.IntegerField(default=0)
    looking_for = models.CharField(max_length=500, blank=True, null=True)
    instagram_access_token = models.CharField(max_length=255, blank=True, null=True)
    instagram_user_id = models.CharField(max_length=255, blank=True, null=True)
    wedding_location = models.CharField(max_length=500, blank=True, null=True)
    secret_id = models.CharField(max_length=500, blank=True, null=True)

    notification_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    budget = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)
    rsvp_count = models.IntegerField(default=0)
    invitation_count = models.IntegerField(default=0)
    bids_count = models.IntegerField(default=0)
    subscribed = models.BooleanField(default=False)

    weekly = models.BooleanField(default=False)
    daily = models.BooleanField(default=False)
    channel = models.BooleanField(default=False)
    direct = models.BooleanField(default=False)


    yelp_location_zip = models.CharField(max_length=50, null=True, blank=True)
    yelp_name = models.CharField(max_length=255, null=True, blank=True)

    def get_yelp_image(self):
        if self.yelp_name and self.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
                                                location = self.yelp_location_zip,
                                                term = self.yelp_name, limit = 10,
                                                sort = YelpClient.SortType.BEST_MATCHED
            )
            print "result: "
            yelp_rating = result_json
            print 'Yelp: ',yelp_rating
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            name_yelp = yelp_rating['businesses'][0]['name']
            name_categories = yelp_rating['businesses'][0]['categories'][0]
            description_yelp = yelp_rating['businesses'][0]['snippet_text']
            return {
                'image_url_yelp':image_url_yelp,
                # 'image_url_yelp':image_url_yelp,
                'name_yelp':name_yelp,
                'name_categories':name_categories,
                'description_yelp':description_yelp,

            }

    def get_yelp_name_categories(self):
        if self.yelp_name and self.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
                                                location = self.yelp_location_zip,
                                                term = self.yelp_name, limit = 10,
                                                sort = YelpClient.SortType.BEST_MATCHED
            )
            print "result: "
            yelp_rating = result_json
            print 'Yelp: ',yelp_rating
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            # name_yelp = yelp_rating['businesses'][0]['name']
            name_categories = yelp_rating['businesses']
            if name_categories:
                name_categories = name_categories[0]['categories'][0]
            # description_yelp = yelp_rating['businesses'][0]['snippet_text']
            cat = ""
            for x in name_categories:
                cat = cat+x+" "
            return cat

    def get_yelp_description(self):
        if self.yelp_name and self.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
                                                location = self.yelp_location_zip,
                                                term = self.yelp_name, limit = 10,
                                                sort = YelpClient.SortType.BEST_MATCHED
            )
            # print "result: "
            yelp_rating = result_json
            # print 'Yelp: ',yelp_rating
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            # name_yelp = yelp_rating['businesses'][0]['name']
            # name_categories = yelp_rating['businesses'][0]['categories'][0]
            description_yelp = yelp_rating['businesses']
            if description_yelp:
                description_yelp = description_yelp[0]['snippet_text']
            return description_yelp

    def get_yelp_image(self):
        if self.yelp_name and self.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
                                                location = self.yelp_location_zip,
                                                term = self.yelp_name, limit = 10,
                                                sort = YelpClient.SortType.BEST_MATCHED
            )
            # print "result: "
            yelp_rating = result_json
            # print 'Yelp: ',yelp_rating
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses']
            if image_url_yelp:
                image_url_yelp = image_url_yelp[0]['rating_img_url_large']
            return image_url_yelp

    def get_yelp_profile_image(self):
        if self.yelp_name and self.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
                                                location = self.yelp_location_zip,
                                                term = self.yelp_name, limit = 10,
                                                sort = YelpClient.SortType.BEST_MATCHED
            )
            # print "result: "
            yelp_rating = result_json
            # print 'Yelp: ',yelp_rating
            # image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses']
            if image_url_yelp:
                try:
                    image_url_yelp = image_url_yelp[0]['image_url']
                except:
                    image_url_yelp = None
            return image_url_yelp

    notification_events = models.BooleanField(default=False)
    notification_tasks = models.BooleanField(default=False)

    last_seen = models.DateTimeField(default=timezone.now())

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)

    """
    New added by Chong
    """
    tag = models.CharField(max_length=128, blank=True, null=True, default="")
    video_url = models.CharField(max_length=512, blank=True, null=True, default="")
    facebook_url = models.CharField(max_length=512, blank=True, null=True, default="")
    twitter_url = models.CharField(max_length=512, blank=True, null=True, default="")
    pinterest_url = models.CharField(max_length=512, blank=True, null=True, default="")
    youtube_url = models.CharField(max_length=512, blank=True, null=True, default="")
    instagram_url = models.CharField(max_length=512, blank=True, null=True, default="")
    yelp_url = models.CharField(max_length=512, blank=True, null=True, default="")

    website_url = models.CharField(max_length=512, blank=True, null=True, default="")


    def check_subscription(self):
        if self.type == UserProfile.PROFESSIONAL:
            try:
                sub_code = SubscriptionCode.objects.get(user=self.user)
                if sub_code.is_subscribed:
                    return True
                else:
                    return False
            except:
                sub_code = SubscriptionCode.objects.create(user=self.user, code=id_generator(size=35))
                return False
        return True

    def __unicode__(self):
        return self.user.username

    def get_full_address(self):
        if self.city == None and self.state == None:
            return "N/A"
        return "%s %s"%(self.city, self.state)

    def get_full_map_address(self):
        if self.city == None and self.state == None:
            return ""
        # return "%s %s %s %s"%(self.street, self.city, self.zip, self.state)
        return "%s %s USA"%(self.city, self.state)
    def get_image_url(self):
        # print "self.image: ",self.image
        if not self.image == "":
            return "%s%s"%(settings.MEDIA_URL, self.image)
        else:
            return "https://yapjoy-static.s3.amazonaws.com/media/media/tempPhoto.png"

    def get_cover_url(self):
        return "%s%s"%(settings.MEDIA_URL, self.cover_image)

    def get_profile_url(self):
        if self.type == self.PROFESSIONAL:
            return "/professional/profile/%d/"%(self.id)
        else:
            return "/profile/%d"%(self.id)

class optionsSearch_users(models.Model):
    open_search = models.ForeignKey('optionsSearch')
    userprofile = models.ForeignKey(UserProfile)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Company(models.Model):

    userprofile = models.OneToOneField(UserProfile, related_name='userprofile_company')
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    payment_terms = models.CharField(max_length=1000, null=True, blank=True)

    SELECT = 'N/A'
    ONEFIVE = '1-5'
    SIXFIFTEEN = '6-15'
    SIXTEENFIFTY = '16-50'
    FIFTYPLUS = '50+'


    EMPLOYEES_OPTIONS = (
        (SELECT, "Select no of Employees"),
        (ONEFIVE, "1-5"),
        (SIXFIFTEEN, "6-15"),
        (SIXTEENFIFTY, "16-50"),
        (FIFTYPLUS, "50+"),
    )
    employees = models.CharField(max_length=50, choices=EMPLOYEES_OPTIONS, default=SELECT)
    subscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Friends(models.Model):
    user = models.ForeignKey(User)
    friends = models.ManyToManyField(User, through='AllFriends', related_name='all_friends')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s'%(self.user)

class AllFriends(models.Model):
    user = models.ForeignKey(User)
    friends = models.ForeignKey(Friends)

    PROFESSIONAL = 'Professional'
    FRIEND = 'Friend'
    TYPE_OPTIONS = (
        (PROFESSIONAL, "Professional"),
        (FRIEND, "Friend"),
    )
    type = models.CharField(max_length=50, choices=TYPE_OPTIONS, default=FRIEND)
    ACCEPTED = 'Accepted'
    PENDING = 'Pending'
    FOLLWOING = 'Following'
    INVITED = 'Invited'
    STATUS_CHOICES = (
        (ACCEPTED, "Friends"),
        (PENDING, "Pending"),
        (FOLLWOING, "Following"),
        (INVITED, "Invited"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Interest(models.Model):
    title = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class PasswordRecover(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=500, null=True, blank=True)

    is_recovered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class optionsSearch(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/options/', null=True, blank=True)
    image_selected = models.ImageField(upload_to='images/options_selected/', null=True, blank=True)
    image_icon = models.ImageField(upload_to='images/options_icon/', null=True, blank=True)

    SHOW = 'Show'
    HIDE = 'Hide'
    STATUS_CHOICES = (
        (SHOW, "Show"),
        (HIDE, "Hide"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=SHOW)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_listings(self):
        from yapjoy_market.models import Product
        return Product.objects.filter(category_id=self.id, isListing=True).count()

class SubscribedUsers(models.Model):
    user = models.ForeignKey(User)
    subscription_date = models.DateTimeField(auto_now_add=True)
    no_of_months = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)

    is_expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # subscription_date.editable = True

class RegisteredBrideUsers(models.Model):
    email = models.CharField(max_length=500, null=True, blank=True)
    is_unsub = models.BooleanField(default=False)
    code = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class SubscriptionCode(models.Model):
    user = models.OneToOneField(User, related_name="sub_code")
    code = models.CharField(max_length=255)
    is_subscribed = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class RegisterRequest(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(max_length=1000, null=True, blank=True)
    wedding_date = models.DateField(null=True, blank=True)
    wedding_location = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

def create_PasswordRecover(sender, instance, created, **kwargs):
    if created:
        instance.code = id_generator()
        instance.save()
post_save.connect(create_PasswordRecover, sender=PasswordRecover)

def create_subscription_code(sender, instance, created, **kwargs):
    if created:
        instance.code = id_generator()
        instance.save()
post_save.connect(create_subscription_code, sender=SubscriptionCode)

def RegisteredBrideUsersSignal(sender, instance, created, **kwargs):
    if created:
        instance.code = id_generator()
        instance.save()
post_save.connect(RegisteredBrideUsersSignal, sender=RegisteredBrideUsers)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        up = UserProfile.objects.create(user=instance, activation_id=id_generator(), dashboard_link="https://www.pinterest.com/baweddingfairs/")
        up.secret_id = id_generator()
        up.save()
post_save.connect(create_user_profile, sender=User)

from yapjoy_accounts.models import Notifications
from .commons import send_email
def AllFriends_notify(sender, instance, created, **kwargs):
    if created:
        profile = instance.user.userprofile
        user = instance.friends.user.get_full_name()
        if instance.status == AllFriends.FOLLWOING:
            Notifications.objects.create(userprofile=profile, message="%s started following you."%(user))
            send_email(instance.user.email, message="%s started following you."%(user), title="New follower", subject="You have a new follower on Yapjoy")
        else:
            Notifications.objects.create(userprofile=profile, message="You have a friends request from %s"%(user))
            send_email(instance.user.email, message="You have a new friend request from %s"%(user), title="New friend request", subject="You have a new friends request on Yapjoy")
post_save.connect(AllFriends_notify, sender=AllFriends)

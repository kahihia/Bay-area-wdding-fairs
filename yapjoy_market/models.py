from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from yapjoy_registration.models import optionsSearch, UserProfile

class SubscriptionPackages(models.Model):
    tokens = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    image = models.ImageField(upload_to='media/subscription/tokens/')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class VendorViewProduct(models.Model):
    id_viewed = models.CharField(max_length=2500, null=True, blank=True)
    id_sent = models.CharField(max_length=2500, null=True, blank=True)
    vendor = models.OneToOneField(User)

    def get_vendor_viewed_list(self):
        if self.id_viewed:
            return list(self.id_viewed.split(','))
        else:
            return []
    def get_vendor_sent_list(self):
        if self.id_sent:
            return list(self.id_sent.split(','))
        else:
            return []
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    ACTIVE = "Active"
    PENDING = "Pending"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (PENDING, "Pending"),
    )
    user = models.ForeignKey(User)
    # bidder = models.ManyToManyField('ProductBidder', related_name='ProductBidder', blank=True)
    def get_id_str(self):
        return str(self.id)
    title = models.CharField(max_length=255, null=True, blank=True)
    dashboard_link = models.CharField(max_length=1000, null=True, blank=True)
    description = models.TextField()
    amount = models.IntegerField(default=0)
    amount_min = models.IntegerField(default=0)

    is_completed = models.BooleanField(default=False)
    isListing = models.BooleanField(default=False)


    status= models.CharField(max_length=20, choices=STATUS_CHOICES,default=ACTIVE)

    end_date = models.DateField(null=True,blank=True)

    category = models.ForeignKey(optionsSearch, null=True, blank=True)

    awarded_to = models.ForeignKey('Pledge', related_name='product_award_to', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_total_questions(self):
        return ProductQuestion.objects.filter(option_search_id=self.category_id).count()

    def get_total_answers(self):
        return ProductAnswer.objects.filter(product_id=self.id).count()

    def calculate_percentage(self):
        if self.get_total_questions():
            percentage = self.get_total_answers() / self.get_total_questions()
            percentage = percentage*100
            return percentage
        else:
            return 0

    def get_progress(self):
        # questions = ProductQuestion.objects.filter(option_search__id=self.category_id)
        # p_answer = ProductAnswer.objects.filter(product__id=self.id,
        #                                      user=self.user_id,
        #                                      product_question__in=questions).count()
        # questions = questions.count()
        # print questions, p_answer
        # if questions and p_answer:
        #     percent = (float(p_answer)/float(questions))*100
        #     return int(percent)
        # else:
        return 0

    def get_progress_left(self):
        return 100 - self.get_progress()
from django.db.models import Sum
class ProductBids(models.Model):
    product = models.ForeignKey(Product)
    vendor = models.ForeignKey(User)
    description = models.TextField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    accepted_date = models.DateField(null=True, blank=True)
    items = models.ManyToManyField('BidItems')

    def get_total(self):
        print 'getting total'
        print 'total amount: ',self.items.all().aggregate(sum=Sum('price'))['sum']
        return self.items.all().aggregate(sum=Sum('price'))['sum']

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class BidItems(models.Model):
    product_bids = models.ForeignKey('ProductBids')
    item = models.TextField(null=True, blank=True)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

import datetime
def get_upload_dish_image_url_s3_file_name(instance, filename):
    now = datetime.datetime.now()

    file_name = str(filename.split('.')[-2]) + '_'+ str(now.year) + '_'+ str(now.month) + '_'+ str(now.second) + '.' + str(filename.split('.')[-1])

    return "media/%s" % (file_name)

class Dream(models.Model):
    product = models.ForeignKey(Product)
    # title = models.CharField(max_length=128)
    image = models.ImageField(upload_to=get_upload_dish_image_url_s3_file_name, default='')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class ProductBudget(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=128)
    budget = models.IntegerField(default=0)

    is_awarded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProductBidder(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    product = models.ForeignKey(Product)
    album = models.ManyToManyField('ProductBidderAlbum', related_name='ProductBidderAlbum', blank=True)

    itemIncluded = models.CharField(max_length=512, default="")

    description = models.CharField(max_length=128)
    budget = models.IntegerField(default=0)

    is_awarded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.userprofile.user.get_full_name()


class ProductBidderAlbum(models.Model):
    bidder = models.ForeignKey(ProductBidder)
    image = models.ImageField(upload_to=get_upload_dish_image_url_s3_file_name, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)



#For the options of the question
class ProductQuestionOption(models.Model):
    question = models.ManyToManyField('ProductQuestion', blank=True, null=True)
    option = models.CharField(max_length=128, default="")

    isDateTime = models.BooleanField(default=False)
    isTextArea = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.option

class ProductQuestion(models.Model):
    option_search = models.ForeignKey(optionsSearch, null=True, blank=True)
    options = models.ManyToManyField(ProductQuestionOption, blank=True, null=True)

    questionSequence = models.IntegerField(default=0)
    # isLastQuestion = models.BooleanField(default=False)
    isAllowMulti = models.BooleanField(default=False)

    title = models.CharField(max_length=128, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProductAnswer(models.Model):
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)
    product_question = models.ForeignKey(ProductQuestion)
    answer = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def split_answers(self):
        if self.answer:
            answer = self.answer.replace(',','<br />')
            print answer
            return answer


class Pledge(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    amount = models.IntegerField(default=0)
    message = models.TextField()

    is_awarded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s"%(self.user, self.amount)

def Pledge_class(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.amount_min += 1
        product.save()
        user = instance.user
        profile = user.userprofile
        profile.bids_count += 1
        profile.save()
post_save.connect(Pledge_class, sender=Pledge)

class RsvpSend(models.Model):
    user= models.ForeignKey(User)
    invited_user= models.ForeignKey(User,related_name='invited_user')
    code = models.CharField(max_length=255)
    status =models.CharField(max_length=255,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class RsvpCount(models.Model):
    user= models.ForeignKey(User)
    rsvp_count = models.IntegerField(default=0)
    rsvp_accepted_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
class RsvpToEmails(models.Model):
    user= models.ForeignKey(User)
    invited_email= models.EmailField()
    code = models.CharField(max_length=255)
    status =models.CharField(max_length=255,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class DemoPlan(models.Model):
    user = models.ForeignKey(User)

    VenueQuestion1 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion2 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion3 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion4 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion5 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion6 = models.CharField(max_length=1000, null=True, blank=True)
    VenueQuestion7 = models.CharField(max_length=1000, null=True, blank=True)
    is_venue_done = models.BooleanField(default=False)
    is_venue_done_taken = models.BooleanField(default=False)

    DjQuestion1 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion2 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion3 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion4 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion5 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion6 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion7 = models.CharField(max_length=1000, null=True, blank=True)
    DjQuestion8 = models.CharField(max_length=1000, null=True, blank=True)
    is_dj_done = models.BooleanField(default=False)
    is_dj_done_taken = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def calculate_percentage(self):
        done = 0
        if self.VenueQuestion1:
            done += 1
        if self.VenueQuestion2:
            done += 1
        if self.VenueQuestion3:
            done += 1
        if self.VenueQuestion4:
            done += 1
        if self.VenueQuestion5:
            done += 1
        if self.VenueQuestion6:
            done += 1
        if self.VenueQuestion7:
            done += 1
        if self.DjQuestion1:
            done += 1
        if self.DjQuestion2:
            done += 1
        if self.DjQuestion3:
            done += 1
        if self.DjQuestion4:
            done += 1
        if self.DjQuestion5:
            done += 1
        if self.DjQuestion6:
            done += 1
        if self.DjQuestion7:
            done += 1
        if self.DjQuestion8:
            done += 1
        percent = (float(done)/15)*100
        return percent

    def calculate_percentage_remaining(self):
        return (100 - self.calculate_percentage())
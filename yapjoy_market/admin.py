from django.contrib import admin
from .models import *
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__email', 'title']
    list_display = ['user','id','title','amount','is_completed','isListing','category','status','created_at']
    raw_id_fields = ['user','awarded_to']
admin.site.register(Product, ProductAdmin)

class ProductBudgetAdmin(admin.ModelAdmin):
    list_display = ['product','id','title','budget','is_awarded','created_at']
    search_fields = ['product']
admin.site.register(ProductBudget, ProductBudgetAdmin)

class ProductQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['option','id', 'isDateTime','isTextArea','created_at']
admin.site.register(ProductQuestionOption, ProductQuestionOptionAdmin)

class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ['id','option_search', 'title', 'questionSequence','isAllowMulti','created_at']
admin.site.register(ProductQuestion, ProductQuestionAdmin)

class ProductAnswerAdmin(admin.ModelAdmin):
    list_display = ['product','id', 'user', 'product_question','answer','created_at']
    raw_id_fields = ['product','product_question','user']
admin.site.register(ProductAnswer, ProductAnswerAdmin)

class DreamAdmin(admin.ModelAdmin):
    list_display = ['product','id','image','created_at']
admin.site.register(Dream, DreamAdmin)

class PledgeAdmin(admin.ModelAdmin):
    list_display = ['user','product','amount','is_awarded','created_at']
admin.site.register(Pledge, PledgeAdmin)
class RsvpSendAdmin(admin.ModelAdmin):
    list_display = ['user','invited_user','code','status','created_at']
admin.site.register(RsvpSend, RsvpSendAdmin)
class RsvpCountAdmin(admin.ModelAdmin):
    list_display = ['user','rsvp_count','rsvp_accepted_count','created_at']
admin.site.register(RsvpCount, RsvpCountAdmin)
class RsvpToEmailsAdmin(admin.ModelAdmin):
    list_display = ['user','invited_email','code','status','created_at']
admin.site.register(RsvpToEmails, RsvpToEmailsAdmin)

class ProductBidderAdmin(admin.ModelAdmin):
    list_display = ['userprofile', 'description','budget', 'is_awarded']
admin.site.register(ProductBidder, ProductBidderAdmin)

class ProductBidderAlbumAdmin(admin.ModelAdmin):
    list_display = ['bidder','image']
admin.site.register(ProductBidderAlbum, ProductBidderAlbumAdmin)
class VendorViewProductAdmin(admin.ModelAdmin):
    list_display = ['vendor','id_viewed','id_sent','created_at']
admin.site.register(VendorViewProduct, VendorViewProductAdmin)
class SubscriptionPackagesAdmin(admin.ModelAdmin):
    list_display = ['tokens','amount','image','created_at']
admin.site.register(SubscriptionPackages, SubscriptionPackagesAdmin)
class ProductBidsAdmin(admin.ModelAdmin):
    list_display = ['product','vendor_id','description','is_accepted','accepted_date','created_at']
admin.site.register(ProductBids, ProductBidsAdmin)
class BidItemsAdmin(admin.ModelAdmin):
    list_display = ['product_bids','item','price','created_at']
admin.site.register(BidItems, BidItemsAdmin)
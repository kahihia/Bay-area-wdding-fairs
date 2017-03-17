from django.contrib import admin
from .models import CreditPackages, TransactionHistory, Transaction, Notifications, Packages
class CreditPackagesAdmin(admin.ModelAdmin):
    list_display = ['title','credits','amount','status','created_at']
admin.site.register(CreditPackages, CreditPackagesAdmin)
class CreditPackagesAdmin(admin.ModelAdmin):
    list_display = ['user','amount','status','transaction_id','created_at']
admin.site.register(Transaction, CreditPackagesAdmin)
class CreditPackagesAdmin(admin.ModelAdmin):
    list_display = ['user','amount','event','created_at']
admin.site.register(TransactionHistory, CreditPackagesAdmin)
class NotificationsAdmin(admin.ModelAdmin):
    # search_fields = ['user__email','user__username']
    list_display = ['userprofile','message','is_read','created_at']
admin.site.register(Notifications, NotificationsAdmin)
class PackagesAdmin(admin.ModelAdmin):
    # search_fields = ['user__email','user__username']
    list_display = ['amount','coins','created_at']
admin.site.register(Packages, PackagesAdmin)
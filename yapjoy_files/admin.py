from django.contrib import admin
from .models import *
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['id','LastName','Email','csvfile','userprofileID']
    search_fields = ['LastName', 'Email']
admin.site.register(UserInfo, UserInfoAdmin)

class WpInfoAdmin(admin.ModelAdmin):
    list_display = ['id','firstname', 'lastname', 'email','amount','date', 'event', 'accept']
    search_fields = ['Email']
admin.site.register(WpInfo, WpInfoAdmin)

class Event_fairsAdmin(admin.ModelAdmin):
    list_display = ['name','is_expired', 'date', 'created_at',]
    search_fields = ['name','date']
admin.site.register(Event_fairs, Event_fairsAdmin)

class Register_EventAdmin(admin.ModelAdmin):
    list_display = ['user','name','business_name', 'event', 'created_at', 'status']
    search_fields = ['name','user__email','user__username','email']
    raw_id_fields = ['user', 'event','sales']
admin.site.register(Register_Event, Register_EventAdmin)

class SalesCommissionAdmin(admin.ModelAdmin):
    list_display = ['sales','amount','is_commission_paid', 'paid_by', 'created_at',]
    raw_id_fields = ['sales', 'paid_by',]
admin.site.register(SalesCommission, SalesCommissionAdmin)

class Invoice_EventAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount','code','status', 'created_at',]
    search_fields = ['amount','user__email','user__username']
admin.site.register(Invoice_Event, Invoice_EventAdmin)

class MediaKitAdmin(admin.ModelAdmin):
    list_display = ['user', 'vendor_name','email','status','code', 'created_at',]
    search_fields = ['email','user__email','user__username','code']
admin.site.register(MediaKit, MediaKitAdmin)


class BulkInvoicesAdmin(admin.ModelAdmin):
    list_display = ['amount','code','status', 'created_at',]
    search_fields = ['amount','email','code']
admin.site.register(BulkInvoices, BulkInvoicesAdmin)

class csvUploadAdmin(admin.ModelAdmin):
    list_display = ['name','is_visible','amount', 'created_at',]
    search_fields = ['name']
admin.site.register(csvUpload, csvUploadAdmin)

class UserCSVAdmin(admin.ModelAdmin):
    list_display = ['user','csv','created_at',]
    search_fields = ['user__username', 'user__email']
admin.site.register(UserCSV, UserCSVAdmin)

class csvDataAdmin(admin.ModelAdmin):
    list_display = ['email','first_name','last_name','created_at',]
    search_fields = ['email', 'first_name','last_name']
admin.site.register(csvData, csvDataAdmin)

class NotesAdmin(admin.ModelAdmin):
    list_display = ['id','exhibitor','note_writer','note']
    search_fields = ['note_writer']
admin.site.register(Notes, NotesAdmin)

class NotesExAdmin(admin.ModelAdmin):
    list_display = ['id','exhibitor','note_writer','note']
    search_fields = ['note_writer']
admin.site.register(NotesEx, NotesExAdmin)

class SalesTasksAdmin(admin.ModelAdmin):
    list_display = ['id','exhibitor','sales','subject', 'message', 'status', 'dueDate']
    search_fields = ['sales']
admin.site.register(SalesTasks, SalesTasksAdmin)
class SalesTasksExAdmin(admin.ModelAdmin):
    list_display = ['id','exhibitor','sales','subject', 'message', 'status', 'dueDate']
    search_fields = ['sales']
admin.site.register(SalesTasksEx, SalesTasksExAdmin)
admin.site.register(CategoryOptions)
class Register_Event_AggrementAdmin(admin.ModelAdmin):
    list_display = ['email','code','status','created_at']
    search_fields = ['code']
    raw_id_fields = ['user','invoices']
admin.site.register(Register_Event_Aggrement, Register_Event_AggrementAdmin)
class EventInvoiceRequestAdmin(admin.ModelAdmin):
    list_display = ['get_email','code','status','type','created_at']
    search_fields = ['code','event_invoice__email']
    raw_id_fields = ['event_invoice']
    def get_email(self, obj):
        return obj.event_invoice.email
admin.site.register(EventInvoiceRequest, EventInvoiceRequestAdmin)
class EventInvoiceAdmin(admin.ModelAdmin):
    list_display = ['email','deposit_date','is_manual', 'created_at']
    # exclude = ['invoices']
    # exclude= ['invoices']
    raw_id_fields = ['register_event','invoices']
    search_fields = ['email']
admin.site.register(EventInvoice, EventInvoiceAdmin)
class EventInvoiceDetailAdmin(admin.ModelAdmin):
    list_display = ['event_invoice','deposit','balance1','balance2','balance3','created_at']
    search_fields = ['event_invoice__email']
    raw_id_fields = ['event_invoice','vendor_register']
admin.site.register(EventInvoiceDetail, EventInvoiceDetailAdmin)
class InvoiceRegisterVendorAdmin(admin.ModelAdmin):
    list_display = ['register','offered_price','is_complete','created_at']
    search_fields = ['register__email','register__name']
    raw_id_fields = ['register','email_list']
admin.site.register(InvoiceRegisterVendor, InvoiceRegisterVendorAdmin)
class Register_Event_InterestedAdmin(admin.ModelAdmin):
    list_display = ['user','name','business_name', 'created_at', 'status']
    search_fields = ['name','user__email','user__username','email']
    raw_id_fields = ['user', 'event','sales']
admin.site.register(Register_Event_Interested, Register_Event_InterestedAdmin)
class Card_change_Admin(admin.ModelAdmin):
    list_display = ['email','code','is_expired', 'created_at']
    search_fields = ['email','code','is_expired','created_at']
admin.site.register(CardChange, Card_change_Admin)

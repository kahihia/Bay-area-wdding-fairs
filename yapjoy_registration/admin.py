from django.contrib import admin
from .models import *
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'type','looking_for','subscribed','state','instagram_access_token','instagram_user_id','created_at']
    search_fields = ['user__username','user__email','state']
    list_filter = ['type']
    raw_id_fields = ['user']
admin.site.register(UserProfile, UserProfileAdmin)
class FriendsAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username', 'user__email']
admin.site.register(Friends, FriendsAdmin)
class AllFriendsAdmin(admin.ModelAdmin):
    search_fields = ['user__username','user__email',]
    list_display = ['user', 'friends','status','type']
admin.site.register(AllFriends, AllFriendsAdmin)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['userprofile', 'name','subscribed']
    search_fields = ['name','userprofile__user__email','userprofile__user__username']
    raw_id_fields = ['userprofile']
admin.site.register(Company, CompanyAdmin)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['title']
admin.site.register(Interest, InterestAdmin)
class PasswordRecoverAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_recovered', 'created_at']
admin.site.register(PasswordRecover, PasswordRecoverAdmin)
class optionsSearchAdmin(admin.ModelAdmin):
    list_display = ['name','image','image_selected','image_icon','status','created_at']
admin.site.register(optionsSearch, optionsSearchAdmin)
class optionsSearch_usersSearchAdmin(admin.ModelAdmin):
    list_display = ['open_search', 'userprofile', 'created_at']
admin.site.register(optionsSearch_users, optionsSearch_usersSearchAdmin)
class SubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_date','no_of_months','amount','is_expired', 'created_at']
admin.site.register(SubscribedUsers, SubscribedUsersAdmin)
class RegisteredBrideUsersAdmin(admin.ModelAdmin):
    search_fields = ['email','code']
    list_display = ['email', 'code','is_unsub','created_at']
admin.site.register(RegisteredBrideUsers, RegisteredBrideUsersAdmin)
class RegisterRequestAdmin(admin.ModelAdmin):
    search_fields = ['name','email']
    list_display = ['name', 'email','wedding_date','wedding_location','created_at']
admin.site.register(RegisterRequest, RegisterRequestAdmin)
import csv
from django.http import HttpResponse
import StringIO
class SubscriptionCodeAdmin(admin.ModelAdmin):
    search_fields = ['user__username','user__email','code']
    list_display = ['user', 'code','is_subscribed','is_registered','created_at']
    raw_id_fields = ['user']

    actions = ['export_code_csv']

    def export_code_csv(self, request, queryset):

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(['email', 'name', 'code'])

        for s in queryset:
            writer.writerow([s.user.email, s.user.get_full_name(), s.code])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=code-info.csv'
        return response

    export_code_csv.short_description = "Export code CSV"
admin.site.register(SubscriptionCode, SubscriptionCodeAdmin)
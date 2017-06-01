from django.contrib import admin
from bayareaweddingfairs_blogs.models import *
# Register your models here.


# class EventFairsDetailsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'eventFair', 'eventUpdate', 'created_at']
#     search_fields = ['eventFair', 'eventUpdate']

admin.site.register(PostModel)
admin.site.register(CategoryModel)
admin.site.register(CommentModel)


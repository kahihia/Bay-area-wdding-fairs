from django.contrib import admin
from bayareaweddingfairs_blogs.models import *
# Register your models here.


class PostsModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'post_slug': ('title',)}
    list_display = ['title', 'post_slug', 'text', 'img']


class CategoryModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'category_slug': ('category_title',)}

admin.site.register(PostModel, PostsModelAdmin)
admin.site.register(CategoryModel,CategoryModelAdmin)


admin.site.register(CommentModel)


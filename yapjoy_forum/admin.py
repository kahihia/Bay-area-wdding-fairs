from django.contrib import admin
from yapjoy_forum.models import Forum, Topic, Post, ProfaneWord, Suggestion

class ForumAdmin(admin.ModelAdmin):
    pass

class TopicAdmin(admin.ModelAdmin):
    list_display = ["title", "forum", "creator", "created"]
    list_filter = ["forum", "creator"]

class PostAdmin(admin.ModelAdmin):
    search_fields = ["title", "creator"]
    list_display = ["title", "topic", "creator", "created"]

class SuggestionAdmin(admin.ModelAdmin):
    search_fields = ["user__username","user__email", "topic"]
    list_display = ["user", "topic", "created_at"]

class ProfaneWordAdmin(admin.ModelAdmin):
    pass

admin.site.register(Suggestion, SuggestionAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ProfaneWord, ProfaneWordAdmin)

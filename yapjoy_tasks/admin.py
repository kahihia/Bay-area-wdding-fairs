from django.contrib import admin
from .models import *

class TaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject','created_at','modified_at']
admin.site.register(Task, TaskAdmin)
class TaskAssignAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'status']
admin.site.register(TaskAssign, TaskAssignAdmin)
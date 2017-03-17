from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    user = models.ForeignKey(User)
    assign = models.ManyToManyField(User, through='TaskAssign', related_name='assign')
    subject = models.CharField(max_length=255)

    due = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(max_length=512)
    complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.subject

class TaskAssign(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)

    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    PENDING = 'Pending'
    STATUS_CHOICES = {
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    }
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
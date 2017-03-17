from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

#unused model for now
class Event(models.Model):
    user = models.ForeignKey(User)
    subject = models.CharField(max_length=255)

    start = models.CharField(max_length=50)
    end = models.CharField(max_length=50)
    all_day = models.BooleanField(auto_created=False)

    include_friends = models.ManyToManyField(User, through='UserEvent', related_name="main_event")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.subject


class UserEvent(models.Model):
   user = models.ForeignKey(User)
   event = models.ForeignKey(Event)

   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)

   def __unicode__(self):
       return self.event




#use this model
class CalendarEvent(models.Model):
    """The event set a record for an
    activity that will be scheduled at a
    specified date and time.

    It could be on a date and time
    to start and end, but can also be all day.

    :param title: Title of event
    :type title: str.

    :param start: Start date of event
    :type start: datetime.

    :param end: End date of event
    :type end: datetime.

    :param all_day: Define event for all day
    :type all_day: bool.
    """
    user = models.ForeignKey(User)
    title = models.CharField(_('Title'), blank=True, max_length=200)
    start = models.DateTimeField(_('Start'))
    end = models.DateTimeField(_('End'))
    all_day = models.BooleanField(_('All day'), default=False)
    is_wedding = models.BooleanField(_('Is Wedding'), default=False)

    assign_event_users = models.ManyToManyField(User, through='CalendarEventUser', related_name='assign_event_users')

    #class Meta:
    #    verbose_name = _('Event')
    #    verbose_name_plural = _('Events')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

class CalendarEventUser(models.Model):
    user = models.ForeignKey(User)
    calendar_event = models.ForeignKey(CalendarEvent)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class HostEvent(models.Model):
    user = models.ForeignKey(User)
    subject = models.CharField(max_length=255)
    location = models.CharField(max_length=50)

    start = models.CharField(max_length=50)
    end = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

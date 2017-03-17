from django.shortcuts import render, HttpResponseRedirect, Http404, render_to_response, HttpResponse
from django.http import HttpResponseRedirect
from yapjoy_registration.models import Friends
from yapjoy_registration.models import AllFriends
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import EventsForm
from .models import *
import json
from django.core.serializers.json import DjangoJSONEncoder
from restless.models import serialize
from fullcalendar.util import events_to_json, calendar_options
from yapjoy_events.models import CalendarEvent

from django.db.models import Q

OPTIONS = """{  timeFormat: "H:mm",
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay',
                },
                allDaySlot: true,
                firstDay: 0,
                weekMode: 'liquid',
                slotMinutes: 15,
                defaultEventMinutes: 30,
                minTime: 8,
                maxTime: 20,
                editable: true,
                dayClick: function(date, allDay, jsEvent, view) {
                    if (allDay) {
                        $('#calendar').fullCalendar('gotoDate', date)
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },

                eventClick: function(event, jsEvent, view) {
                    if (view.name == 'month') {
                        $('#calendar').fullCalendar('gotoDate', event.start)
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },
            }"""
from django.shortcuts import get_object_or_404


@login_required(login_url='/login/')
def events(request):
    user = request.user
    profile = user.userprofile
    events_all = CalendarEvent.objects.filter(Q(user=user)|Q(assign_event_users__in=User.objects.filter(id=user.id))).distinct().select_related('user').order_by('created_at')

    events_form = EventsForm()
    if request.method == "POST":
        print 'inside request.post'
        if "event_to_delete" in request.POST:
            id = request.POST.get('event_to_delete')
            CalendarEvent.objects.get(id=id, user=request.user).delete()
            return HttpResponse('success')
        else:
            events_form = EventsForm(request.POST)
            if events_form.is_valid():
                data = events_form.cleaned_data
                subject = data['subject']
                start = data['start']
                end = data['end']
                all_day = data['all_day']
                assigned_to = request.POST.getlist('assigned_to')
                print assigned_to

                tmp_e = CalendarEvent.objects.create(
                    user=request.user,
                    title=subject,
                    start=start,
                    end=end,
                    all_day=all_day,
                    )
                for user_assign_id in assigned_to:
                    cal_even = CalendarEventUser.objects.create(user_id=user_assign_id, calendar_event=tmp_e)
                    from yapjoy_registration.models import Notifications
                    from yapjoy_registration.commons import send_email
                    Notifications.objects.create(userprofile=cal_even.user.userprofile, message="%s has invited to an event."%(request.user.get_full_name()))
                    if profile.notification_events:
                        send_email(cal_even.user.email, message="%s has invited to an event."%(request.user.get_full_name()), title="You have been invited to an event.", subject="You have been invited to an event on Yapjoy")
                return HttpResponseRedirect('/events/')
    profile = user.userprofile
    friends = None
    # try:
    #     friends = Friends.objects.get(user=user).friends.all()
    # except:
    #     friends = Friends.objects.create(user=user)
    #     friends = friends.friends.all()
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')#.values('user','friends','friends__user')
    context = {
        'events_form': events_form,
        'events_all': events_all,
        'friends': friends,
        'profile': profile,
        'user': user,
        'jquery_min': True,
        'calendar_config_options': calendar_options('all_events/', OPTIONS),
    }

    return render(request, 'vendroid/events/events.html', context)

@login_required(login_url='/login/')
def events_edit(request, id):
    edited = None
    user = request.user
    profile = user.userprofile
    event = get_object_or_404(CalendarEvent, pk=id, user=user)
    initial = {
        'subject':event.title,
        'start':event.start,
        'end':event.end,
        'all_day':event.all_day,
    }
    events_form = EventsForm(initial=initial)
    if request.method == "POST":

        events_form = EventsForm(request.POST)
        if events_form.is_valid():
            print 'form is valid'
            data = events_form.cleaned_data
            title = data['subject']
            start = data['start']
            end = data['end']
            all_day = data['all_day']
           # assigned_to = request.POST.getlist('assigned_to')
           #  print assigned_to
            event = get_object_or_404(CalendarEvent, pk=id, user=user)
            event.title = title
            event.start = start
            event.end = end
            event.all_day = all_day
            event.save()
            all_users = event.assign_event_users.all()
            print 'all: ',all_users
            if all_users:
                c = CalendarEventUser.objects.filter(user__in=all_users, calendar_event=event).delete()
                print 'all c: ',c
            assigned_to = request.POST.getlist('assigned_to')
           # print len(assigned_to)
            if event.is_wedding == True:
                profile = user.userprofile
                profile.rsvp_count = len(assigned_to)
                profile.wedding_date = start
                profile.save()
            for user_assign_id in assigned_to:
                cal_even = CalendarEventUser.objects.create(user_id=user_assign_id, calendar_event=event)
                from yapjoy_registration.models import Notifications
                from yapjoy_registration.commons import send_email
                Notifications.objects.create(userprofile=cal_even.user.userprofile, message="%s has invited to an event."%(request.user.get_full_name()))
                if profile.notification_events:
                    send_email(cal_even.user.email, message="%s has invited to an event."%(request.user.get_full_name()), title="You have been invited to an event.", subject="You have been invited to an event on Yapjoy")

            edited = 'success'
    profile = user.userprofile
    friends = None
    # try:
    #     friends = Friends.objects.get(user=user).friends.all().distinct()
    # except:
    #     friends = Friends.objects.create(user=user)
    #     friends = friends.friends.all().distinct()
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')
    friends_assigned = event.assign_event_users.all().select_related('userprofile','userprofile__user')
    friends = friends.exclude(user_id__in=friends_assigned)
    context = {
        'events_form': events_form,
        'profile': profile,
        'edited': edited,
        'friends': friends,
        'friends_assigned': friends_assigned,
    }

    return render(request, 'events/edit_event.html', context)
def all_events(request):
     events_all = CalendarEvent.objects.filter(user=request.user).values('title', 'start', 'end', 'all_day')
     return HttpResponse(events_to_json(events_all), content_type='application/json')


#@login_required(login_url='/login/')
def delete_events(request, id_to_delete):
    if "id_to_delete" in request.POST:
        event = CalendarEvent.objects.get(id=id_to_delete, user=request.user, is_wedding=False).delete()

    return HttpResponseRedirect("/events/")

from django.shortcuts import render, HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login as auth_login
from .forms import *
from yapjoy.settings import SITE_NAME
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from yapjoy_feed.models import *
from yapjoy_messages.models import Feedback
from yapjoy_registration.models import Friends
from .models import *
from django.db.models import Q
from yapjoy_accounts.models import Notifications
from django.shortcuts import get_object_or_404
from django.db.models import Q
from yapjoy_messages.models import *
from yapjoy_market.models import *
import re
from django.views.decorators.csrf import csrf_exempt
from fullcalendar.util import events_to_json, calendar_options
from yapjoy_events.views import OPTIONS
from yapjoy_forum.models import Topic
import stripe
from yapjoy import settings
from billing import CreditCard, get_gateway
from django.core.urlresolvers import reverse

@csrf_exempt
def EmailStep(request):
    error = None
    if request.method == "POST":
        email = request.POST.get('email')
        user = None
        if email:
            try:
                user = User.objects.get(email__iexact=email)
            except:
                user = User.objects.create(email=email, username=email)
            DemoPlan.objects.get_or_create(user=user)
            return HttpResponseRedirect(reverse("SelectStepVer2", kwargs={'id': user.id}))
        error = "Enter an email"
    return render(request, 'vendroid/demov2/email.html',{
        'error':error,
                })

@csrf_exempt

def SelectStep(request, id):
    print 'id is: ',id
    dp =  DemoPlan.objects.get(user_id=id)
    if request.method == "POST":
        survey = request.POST.get('survey')
        print survey
        distinct_surveys = list()
        map(lambda x: not x in distinct_surveys and distinct_surveys.append(x), survey.split(","))
        print distinct_surveys
        if "venue" in distinct_surveys:
            dp.is_venue_done = True
            if 'dj' in distinct_surveys:
                dp.is_dj_done = True
            dp.save()
            return HttpResponseRedirect(reverse("PlansStep", kwargs={'id': id, 'type': 'venue'}))
        if "dj" in distinct_surveys:
            dp.is_dj_done = True
            dp.save()
            return HttpResponseRedirect(reverse("PlansStep", kwargs={'id': id, 'type':'dj'}))
    return render(request, 'vendroid/demo/select.html',{
                })

def PlansStep(request, id, type):
    demoplan = DemoPlan.objects.get(user_id=id)
    list_dj = []
    if type == 'dj':
        list_dj = ['aceentertainment510@gmail.com','niall@fourleafent.com']
    elif type == 'venue':
        list_dj = ['specialevents@lecolonialsf.com', 'katie@geyservilleinn.com','Justin.Martinez@interstatehotels.com','dmtwig@gmail.com','apatrick@berkeleycityclub.com']
    recommendations = UserProfile.objects.filter(user__email__in=list_dj)#[:10]
    context = {
        'demoplan':demoplan,
        'type':type,
        'id':id,
        'type':type,
        'recommendations':recommendations,
    }
    return render(request, 'vendroid/demo/plans.html', context)

def PlansResult(request, id, type):
    demoplan = DemoPlan.objects.get(user_id=id)
    list_dj = []
    if type == 'dj':
        list_dj = ['aceentertainment510@gmail.com','niall@fourleafent.com']
    elif type == 'venue':
        list_dj = ['specialevents@lecolonialsf.com', 'katie@geyservilleinn.com','Justin.Martinez@interstatehotels.com','dmtwig@gmail.com','apatrick@berkeleycityclub.com']
    recommendations = UserProfile.objects.filter(user__email__in=list_dj)#[:10]
    context = {
        'demoplan':demoplan,
        'type':type,
        'id':id,
        'type':type,
        'recommendations':recommendations,
    }
    return render(request, 'vendroid/demo/result.html', context)

@csrf_exempt
def QuestionDJ(request, id, qno):
    demoplan = DemoPlan.objects.get(user_id=id)
    template_name = ""
    if qno == '1':
        template_name = "vendroid/demo/DjQuestions/Question1.html"
    elif qno == '2':
        template_name = "vendroid/demo/DjQuestions/Question2.html"
    elif qno == '3':
        template_name = "vendroid/demo/DjQuestions/Question3.html"
    elif qno == '4':
        template_name = "vendroid/demo/DjQuestions/Question4.html"
    elif qno == '5':
        template_name = "vendroid/demo/DjQuestions/Question5.html"
    elif qno == '6':
        template_name = "vendroid/demo/DjQuestions/Question6.html"
    elif qno == '7':
        template_name = "vendroid/demo/DjQuestions/Question7.html"
    elif qno == '8':
        template_name = "vendroid/demo/DjQuestions/Question8.html"
    print 'id, Qno is: ',id, qno
    if "surveyDJ" in request.POST:
        surveyDJ = request.POST.get('surveyDJ')
        if surveyDJ == "1":
            #----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion1 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.DjQuestion1 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion1 = demoplan.DjQuestion1 + other
            print "final: ",demoplan.DjQuestion1
            if not demoplan.DjQuestion1:
                demoplan.DjQuestion1 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "2":
            #----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion2 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.DjQuestion2 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion2 = demoplan.DjQuestion2 + other
            print "final: ",demoplan.DjQuestion2
            if not demoplan.DjQuestion2:
                demoplan.DjQuestion2 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "3":
            #----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion3 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.DjQuestion3 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion3 = demoplan.DjQuestion3 + other
            print "final: ",demoplan.DjQuestion3
            if not demoplan.DjQuestion3:
                demoplan.DjQuestion3 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "4":
            #----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion4 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.DjQuestion4 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion4 = demoplan.DjQuestion4 + other
            print "final: ",demoplan.DjQuestion4
            if not demoplan.DjQuestion4:
                demoplan.DjQuestion4 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "5":
            #----- with select field -----
            zip = request.POST.get('zip')
            demoplan.DjQuestion5 = ""
            demoplan.DjQuestion5 = zip
            print "final: ",demoplan.DjQuestion5
            if not demoplan.DjQuestion5:
                demoplan.DjQuestion5 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "6":
            # ----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion6 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.DjQuestion6 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion6 = demoplan.DjQuestion6 + other
            print "final: ", demoplan.DjQuestion6
            if not demoplan.DjQuestion6:
                demoplan.DjQuestion6 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "7":
            # ------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion7 = ""
            for o in venue_select:
                if not o == "Yes":
                    demoplan.DjQuestion7 += o + ", "
            print venue_select
            if "Yes" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion7 = demoplan.DjQuestion7 + other
            print "final: ", demoplan.DjQuestion7
            if not demoplan.DjQuestion7:
                demoplan.DjQuestion7 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionDJ", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "8":
            # ------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.DjQuestion8 = ""
            for o in venue_select:
                if not o == "Yes":
                    demoplan.DjQuestion8 += o + ", "
            print venue_select
            if "Yes" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.DjQuestion8 = demoplan.DjQuestion8 + other
            print "final: ", demoplan.DjQuestion8
            if not demoplan.DjQuestion8:
                demoplan.DjQuestion8 = "no response"
            demoplan.is_dj_done_taken = True
            demoplan.save()
            return HttpResponseRedirect(reverse("PlansResult", kwargs={'id': id, 'type': 'dj'}))
        else:
            return HttpResponseRedirect(reverse("PlansResult", kwargs={'id': id,'type':'dj'}))
    return render(request, template_name, {
    })


@csrf_exempt
def QuestionVenue(request, id, qno):
    demoplan = DemoPlan.objects.get(user_id=id)
    template_name = ""
    if qno == '1':
        template_name = "vendroid/demo/VenueQuestions/Question1.html"
    elif qno == '2':
        template_name = "vendroid/demo/VenueQuestions/Question2.html"
    elif qno == '3':
        template_name = "vendroid/demo/VenueQuestions/Question3.html"
    elif qno == '4':
        template_name = "vendroid/demo/VenueQuestions/Question4.html"
    elif qno == '5':
        template_name = "vendroid/demo/VenueQuestions/Question5.html"
    elif qno == '6':
        template_name = "vendroid/demo/VenueQuestions/Question6.html"
    elif qno == '7':
        template_name = "vendroid/demo/VenueQuestions/Question7.html"
    print 'id, Qno is: ',id, qno
    if "surveyVenue" in request.POST:
        surveyDJ = request.POST.get('surveyVenue')
        # if surveyDJ in ['1','2','3','4','5','6',]:
        #     return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "1":
            #----- with select field -----
            venue_select = request.POST.getlist('venue_select')
            demoplan.VenueQuestion1 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.VenueQuestion1 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.VenueQuestion1 = demoplan.VenueQuestion1 + other
            print "final: ",demoplan.VenueQuestion1
            if not demoplan.VenueQuestion1:
                demoplan.VenueQuestion1 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "2":
            #------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.VenueQuestion2 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.VenueQuestion2 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.VenueQuestion2 = demoplan.VenueQuestion2 + other
            print "final: ",demoplan.VenueQuestion2
            if not demoplan.VenueQuestion2:
                demoplan.VenueQuestion2 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "3":
            #------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.VenueQuestion3 = ""
            for o in venue_select:
                if not o == "Other":
                    demoplan.VenueQuestion3 += o + ", "
            print venue_select
            if "Other" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.VenueQuestion3 = demoplan.VenueQuestion3 + other
            print "final: ",demoplan.VenueQuestion3
            if not demoplan.VenueQuestion3:
                demoplan.VenueQuestion3 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "4":
            demoplan.VenueQuestion4 = ""
            #------with checkbox field-------
            date_data = request.POST.get('date_data')
            hour_data = request.POST.get('hour_data')
            print (date_data, hour_data)
            if date_data and hour_data:
                demoplan.VenueQuestion4 = "On %s for %s hours"%(date_data, hour_data)
            print "final: ",demoplan.VenueQuestion4
            if not demoplan.VenueQuestion4:
                demoplan.VenueQuestion4 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "5":
            demoplan.VenueQuestion5 = ""
            #------with checkbox field-------
            miles = request.POST.get('miles')
            zip_code = request.POST.get('zip-code')
            print (miles, zip_code)
            if miles and zip_code:
                demoplan.VenueQuestion5 = "%s miles from %s"%(miles, zip_code)
            print "final: ",demoplan.VenueQuestion5
            if not demoplan.VenueQuestion5:
                demoplan.VenueQuestion5 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "6":
            # ------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.VenueQuestion6 = ""
            for o in venue_select:
                if not o == "Yes":
                    demoplan.VenueQuestion6 += o + ", "
            print venue_select
            if "Yes" in venue_select:
                other = request.POST.get('other')
                print other
                demoplan.VenueQuestion6 = demoplan.VenueQuestion6 + other
            print "final: ", demoplan.VenueQuestion6
            if not demoplan.VenueQuestion6:
                demoplan.VenueQuestion6 = "no response"
            demoplan.save()
            return HttpResponseRedirect(reverse("QuestionVenue", kwargs={'id': id, 'qno':(int(qno)+1)}))
        if surveyDJ == "7":
            # ------with checkbox field-------
            venue_select = request.POST.getlist('venue_select')
            demoplan.VenueQuestion7 = ""
            for o in venue_select:
                if not o == "Yes":
                    demoplan.VenueQuestion7 += o + ", "
            print venue_select
            # if "Yes" in venue_select:
            #     other = request.POST.get('other')
            #     print other
            #     demoplan.VenueQuestion6 = demoplan.VenueQuestion6 + other
            print "final: ", demoplan.VenueQuestion7
            if not demoplan.VenueQuestion7:
                demoplan.VenueQuestion7 = "no response"
            demoplan.is_venue_done_taken = True
            demoplan.save()
            return HttpResponseRedirect(reverse("PlansResult", kwargs={'id': id,'type':'venue'}))
        else:
            return HttpResponseRedirect(reverse("PlansResult", kwargs={'id': id,'type':'venue'}))

    return render(request, template_name,{
                })
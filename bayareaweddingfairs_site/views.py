from django.shortcuts import render
from .models import *
from yapjoy_files.forms import bg_registration_form, registration_event_form, LasVegasForm
from django.contrib.auth.models import User
from yapjoy_registration.models import UserProfile, Company
from yapjoy_files.models import Register_Event_Interested
from yapjoy_files.models import Register_Event, CategoryOptions
from django.shortcuts import HttpResponseRedirect, get_object_or_404, HttpResponse
from yapjoy_files.views import send_bawf_email
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from yapjoy_files.models import Event_fairs
from datetime import datetime
from django.core.urlresolvers import reverse
import json

def Index(request):
    return render(request, "bayareaweddingfairs/site/home/home.html")

def ShopVendors(request):
    vendorShopsList = []
    vendorShops = ShopVendor.objects.all()
    for shop in vendorShops:
        shopItemList = ShopVendorsItem.objects.filter(shopVendors=shop).order_by('created_at')
        vendorShop = {
            'shop': shop,
            'itemsList': shopItemList
        }
        vendorShopsList.append(vendorShop)

    context = {
        'vendorShops': vendorShops,
        'vendorShopsList': vendorShopsList
    }
    return render(request, "bayareaweddingfairs/site/shopVendors/index.html", context)

@csrf_exempt
def OurShows(request):
    if "event_id" in request.POST:
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event_fairs, id=event_id)
        if event:
            data = {
                'description':event.description,
                'description_grand':event.grandPrizeDescription,
                'image':str(event.image),
                'name':event.name,
                'location':event.location,
                'date':str(event.date),
            }
            return HttpResponse(json.dumps(data))
    events_list = Event_fairs.objects.filter(date__gte=datetime.now(), is_expired=False)
    events = sort_months(events_list)
    return render(request, "bayareaweddingfairs/site/ourShows/ourShows.html", {
        'events':events,
    })

def sort_months(events):
    January, February, March, April, May, June, July, August, September, October, November, December = ([] for i in range(12))
    list_months = ['', January, February, March, April, May, June, July, August, September, October, November, December]
    for event in events:
        list_months[event.date.month].append(event)
    return list_months

@csrf_exempt
def BrideGroomRegistration(request):
    error_message = None
    eventsIDList = None
    cat = ""
    eventsCheck = None
    how_heard = None
    inteventsIDList = None
    form = bg_registration_form()
    if request.method == "POST":
        form = bg_registration_form(request.POST)
        event_name = ""
        how_heard = None
        eventsIDList = request.POST.getlist('eventsCheck')
        how_heard = request.POST.get('how_heard')
        inteventsIDList = []
        if eventsIDList:
            for x in eventsIDList:
                inteventsIDList.append(int(x))
        else:
            eventsCheck = "Select an event atleast"
        if form.is_valid():
            data = form.cleaned_data
            if eventsIDList:
                firstName = data['firstName']
                lastName = data['lastName']
                phone = data['phone']
                email = data['email']
                city = data['city']
                zip = data['zip']
                comments = data['comments']
                how_heard = data['how_heard']
                categories = data['categories']
                name = firstName + " " + lastName
                try:
                    weddingDate = data['weddingDate']
                except:
                    weddingDate = ''
                user_reg = None
                reg = None
                try:
                    user_reg = User.objects.get(email__iexact=email)
                except:
                    user_reg = User.objects.create(email=email, username=email)
                    profile = UserProfile.objects.get(user=user_reg)
                    profile.type = UserProfile.PROFESSIONAL
                    profile.save()
                for eID in eventsIDList:
                    event = Event_fairs.objects.get(id=eID)
                    cat = ""
                    for c in categories:
                        cat += "%s " % (c)
                    reg = Register_Event.objects.create(
                        user=user_reg,
                        name=name,
                        phone=phone,
                        email=user_reg.email,
                        city=city,
                        zip=zip,
                        comments=comments,
                        how_heard=how_heard,
                        event=event,
                        weddingDate=weddingDate,
                        type=Register_Event.BGUSER,
                    )
                    event_name += "%s - %s<br />" % (event.name, event.date)
                    for cat in categories:
                        try:
                            ca = CategoryOptions.objects.get(category__iexact=cat)
                            reg.categories.add(ca)
                        except:
                            pass
                message = "Thank you for registering with Bay Area Wedding Fairs.<br /><br />%s<br /><br />If you like to save time and money, pre-pay online at <a href='http://bayareaweddingfairs.com/bridegroomtestregistration/'>https://bayareaweddingfairs.com/bridegroomtestregistration/</a>. Also, we encourage you to go to our <a href='https://www.facebook.com/baweddingfairs/events'>Facebook Events Page</a>, select the Fair and click on 'Join'. You will be entered in our weekly 'Las Vegas Giveaway' drawing (Winner will be announced on our Facebook page). <br /><br />NEED HELP IN PLANNING? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />if you have any questions, please email us at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com </a><br /><br />We look forward to seeing you at the Wedding Fair<br /><br />Thank You!<br /><br />Bay Area Wedding Fairs" % (
                    event_name)
                send_bawf_email(sendTo=user_reg.email, message=message, title="",
                                subject="Registration Successful!")
                message_information = "First Name: %s<br />Last Name: %s<br />Email: %s<br />Phone: %s<br />City: %s<br />Zip: %s<br />Wedding Fair Interested In: <br />%s<br />Wedding Professional Interested in: %s<br />How do you hear about us: %s<br />Comments: %s<br />" % (
                firstName, lastName, email, phone, city, zip, event_name, cat, how_heard, comments)
                send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message_information, title="",
                                subject="Bride / Groom Registration Information!")
                return HttpResponseRedirect(reverse("index__bride_registration__success"))
            else:
                error_message = "Select an event atleast"
                eventsCheck = "Select an event atleast"
        else:
            error_message = "Form is not valid: ", form.errors
    """
    converging events by season
    """
    events = Event_fairs.objects.filter(Q(is_expired=False)).order_by('date')
    content = {
        'form': form,
        'events': events,
        'error_message': error_message,
        'eventsIDList': eventsIDList,
        'inteventsIDList': inteventsIDList,
        'eventsCheck': eventsCheck,
        'all_events': events,
        'how_heard': how_heard,
    }
    return render(request, "bayareaweddingfairs/site/BGRegister/BGRegister.html", content)

def VendorRegistrationIndex(request):
    return HttpResponse('Awaiting')

@csrf_exempt
def VendorRegistration(request):
    is_completed = None
    error_message = None
    eventsIDList = None
    inteventsIDList = None
    eventsCheck = None
    how_heard = None
    form = registration_event_form()

    if request.method == "POST":
        form = registration_event_form(request.POST)
        eventsIDList = request.POST.getlist('eventsCheck')
        how_heard = request.POST.get('how_heard')
        inteventsIDList = []
        if eventsIDList:
            for x in eventsIDList:
                inteventsIDList.append(int(x))
        else:
            eventsCheck = "Select an event atleast"
        if form.is_valid():
            data = form.cleaned_data
            if eventsIDList:
                name = data['name']
                business_name = data['business_name']
                phone = data['phone']
                email = data['email']
                city = data['city']
                zip = data['zip']
                comments = data['comments']
                how_heard = data['how_heard']
                category = data['category']
                categories = data['categories']
                website = data['website']
                user_reg = None
                try:
                    user_reg = User.objects.get(email__iexact=email)
                except:
                    user_reg = User.objects.create(email=email, username=email)
                    profile = UserProfile.objects.get(user=user_reg)
                    profile.type = UserProfile.PROFESSIONAL
                    profile.save()
                    Company.objects.create(userprofile=profile, name=business_name)
                event_name = ""
                reg = Register_Event_Interested.objects.create(
                                                        user=user_reg,
                                                        name=name,
                                                        business_name=business_name,
                                                        phone=phone,
                                                        email=user_reg.email,
                                                        city=city,
                                                        zip=zip,
                                                        comments=comments,
                                                        how_heard=how_heard,
                                                        category=categories,
                                                        type=Register_Event.CONTRACTOR,
                                                        website=website,
                                                        )
                for eID in eventsIDList:
                    event = Event_fairs.objects.get(id=eID)
                    reg.event.add(event)
                    event_name += "%s<br />"%(event.name)
                message2 = """<b>Fullname</b> : %s<br /><br />
                        <b>Email</b> : %s<br /><br />
                        <b>Phone</b> : %s<br /><br />
                        <b>City</b> : %s<br /><br />
                        <b>Zipcode</b> : %s<br /><br />
                        <b>Buisness Category</b> : %s<br /><br />
                        <b>Buisness Name</b> : %s<br /><br />
                        <b>Wedding Fair Interested In</b> :<br />
                        %s<br /><br />
                        <b>How did you hear about us</b> : %s<br /><br />
                        <b>Comments</b> : %s"""%(name, user_reg.email, phone, city, zip, categories, business_name, event_name, how_heard, comments)
                send_bawf_email(sendTo="steve@bayareaweddingfairs.com", message=message2, title="Registered Vendor Information:", subject="A NEW VENDOR HAS REGISTERED")
                message = "Thank you for registering with Bay Area Wedding Fairs. We will get back to you soon.<br /><br />LOOKING FOR MORE WEDDING BUSINESS?? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />If you have any questions, please email us directly at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com</a><br /><br />Thank You!<br /><br />Bay Area Wedding Fairs"
                send_bawf_email(sendTo=user_reg.email, message=message, title="", subject="Registration Successful!")
                is_completed = True
                return HttpResponseRedirect(reverse("index__vendor_registration__success"))
            else:
                error_message = "Select an event atleast"
    events = Event_fairs.objects.filter(Q(is_expired=False)&Q(date__gte=datetime.now())).order_by('date')
    content = {
        'form':form,
        'events':events,
        'error_message':error_message,
        'eventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'is_completed':is_completed,
        'how_heard':how_heard,
    }
    return render(request, 'bayareaweddingfairs/site/WPRegister/WPRegister.html', content)

def BecomeExhibitor(request):
    return render(request, "bayareaweddingfairs/site/become_exhibitor/become-an-exhibitor.html")

def VendorRegistrationThankYou(request):
    return render(request, "bayareaweddingfairs/site/become_exhibitor/thank_you.html")

def BrideRegistrationThankYou(request):
    return render(request, "bayareaweddingfairs/site/BGRegister/thank_you.html")

@csrf_exempt
def LasVegasSignin(request):
    error_message = None
    success_message = ""
    form = LasVegasForm()
    if request.method == "POST":
        print "inside post"
        form = LasVegasForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            firstName = data['firstName']
            lastName = data['lastName']
            email = data['email']
            weddingDate = data['weddingDate']
            name = str(firstName) + ' ' + str(lastName)
            user = None
            try:
                user = User.objects.get(email__iexact=email)
            except:
                user = User.objects.create(email=email, username=email, first_name=firstName, last_name=lastName)
            user_reg = Register_Event.objects.create(
                event=Event_fairs.objects.filter(date__gte=datetime.now()).order_by('date')[0],
                user=user,
                name=name,
                email=email,
                is_lasVegasSignIn=True,
                type=Register_Event.BGUSER,
                )
            print "saving las vegas reg"
            success_message = "Your request is submitted successfully."
            message = "Thank you for registering with Bay Area Wedding Fairs.<br /><br />If you have any questions, please email us at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com </a><br /><br />Thank You!<br />Bay Area Wedding Fairs"
            send_bawf_email(sendTo=user_reg.email, message=message, title="",
                            subject="Registration Successful!")
            message_information = "First Name: %s<br />Last Name: %s<br />Email: %s<br /><br />Wedding Date: %s<br /><br />" % (
                firstName, lastName, email, weddingDate)
            send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message_information, title="",
                            subject="Bride / Groom Registration Information!")
            form = LasVegasForm()
        else:
            error_message = "Select an event atleast"
    content = {
        'form': form,
        'success_message': success_message,
    }
    return render(request, 'bayareaweddingfairs/site/lasVegasSignin/LasVegasSignIn.html', content)


def shopDetail(request, id):
    """replace the id with slug"""
    item = get_object_or_404(ShopVendorsItem, id=id)
    itemDetail = ShopVendorsItemDetail.objects.filter(vendorItems=item)

    context = {
        'item': item,
        'detail': itemDetail
    }
    return render(request, "bayareaweddingfairs/shopVendors/shopVendorItemDetail.html", context)
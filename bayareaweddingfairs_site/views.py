from django.shortcuts import render
from .models import *
from yapjoy_files.forms import bg_registration_form
from django.contrib.auth.models import User
from yapjoy_registration.models import UserProfile
from yapjoy_files.models import Register_Event, CategoryOptions
from django.shortcuts import HttpResponseRedirect
from yapjoy_files.views import send_bawf_email
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from yapjoy_files.models import Event_fairs
from datetime import datetime

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

def OurShows(request):
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
                return HttpResponseRedirect('/crm/registration/bg/success/iframe/')
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

def VendorRegistration(request):
    pass
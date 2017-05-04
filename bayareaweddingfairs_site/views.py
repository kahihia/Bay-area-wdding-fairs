from django.shortcuts import render
from .models import *
from yapjoy_files.forms import *
from django.contrib.auth.models import User
from yapjoy_registration.models import UserProfile, Company
from yapjoy_files.models import Register_Event_Interested
from yapjoy_registration.models import UserProfile
from yapjoy_registration.commons import id_generator
from yapjoy_files.models import Register_Event, CategoryOptions
from django.shortcuts import HttpResponseRedirect, get_object_or_404, HttpResponse
from yapjoy_files.views import send_bawf_email
from bayareaweddingfairs_tickets.views import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from yapjoy_files.models import Event_fairs
from datetime import datetime
from django.core.urlresolvers import reverse
import json, stripe, pyqrcode, boto


def Index(request):
    vendorShopsList = []
    vendorShops = ShopVendor.objects.all()
    for shop in vendorShops:
        shopItemList = ShopVendorsItem.objects.filter(shopVendors=shop).order_by('created_at')
        vendorShop = {
            'shop': shop,
            'itemsList': shopItemList
        }
        vendorShopsList.append(vendorShop)
    events_list = Event_fairs.objects.filter(date__gte=datetime.now(), is_expired=False)
    events = sort_months(events_list)
    context = {
        'vendorShops': vendorShops,
        'vendorShopsList': vendorShopsList,
        'events': events,
    }
    return render(request, "bayareaweddingfairs/site/home/home.html", context)

@csrf_exempt
def ContactView(request):
    if request.method == "POST":
        name = request.POST.get('widget-contact-form-name')
        email = request.POST.get('widget-contact-form-email')
        subject = request.POST.get('widget-contact-form-subject')
        message_rec = request.POST.get('widget-contact-form-message')
        Contact.objects.create(email=email, name=name, message=message_rec, subject=subject)
        message = "Subject: %s,<br /><br />You have been contacted by %s. Their message is:<br /><br />%s<br /><br />You can contact %s via email at %s" % (
            subject, name, message_rec, name, email)
        send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message, title="Message submitted successfully.",
                        subject="You have been contacted by %s - BayAreaWeddingFairs" % (name))
        message = "Dear %s,<br /><br />Your request has been submitted. Our representative will get back to you shortly depending upon the sent request.<br /><br />Best<br />BayAreaWeddingFairs" % (
            name)
        send_bawf_email(sendTo=email, message=message, title="",
                        subject="Contact us submission successfull.")
        return HttpResponse(json.dumps({
            'response':'success',
        }))
    return render(request, "bayareaweddingfairs/site/contact/Contact.html")

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
    if request.method == "POST":
        if "event_id" in request.POST:
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event_fairs, id=event_id)
            if event:
                data = {
                    'description':event.description,
                    'description_grand':event.grandPrizeDescription,
                    'footerdetail':event.footerDescription,
                    'image':str(event.image),
                    'name':event.name,
                    'short_location':event.short_location,
                    'geo_location':event.google_location,
                    'location':event.location,
                    'date':str(event.date.strftime('%m-%d-%Y')),
                    'id':event.id,
                }
                return HttpResponse(json.dumps(data))
        elif "optionsRadios" in request.POST:
            optionsRadios = request.POST.get('optionsRadios')
            email = request.POST.get('widget-subscribe-form-email')
            if email and optionsRadios:
                if not Subscriptions.objects.filter(email__iexact=email):
                    Subscriptions.objects.create(email=email, type=optionsRadios, is_subscribed=True)
                    send_bawf_email(sendTo=email, message="You have been successfully subscribed to Bay Area Wedding Fairs Newsletter with email %s."%(email),
                                    title="Bay Area Wedidng Fairs subscription successfull.:", subject="Subscription successfull")
                    send_bawf_email(sendTo="info@bayareaweddingfairs.com",
                                    message="You have been successfully subscribed to Bay Area Wedding Fairs Newsletter with email %s."%(email),
                                    title="Bay Area Wedidng Fairs subscription successfull.:",
                                    subject="Subscription successfull")
                    return HttpResponse(json.dumps({'response':'success'}))
                else:
                    return HttpResponse(json.dumps({
                        'response':'failed',
                        'message':'You are already subscribed for notifications.',
                    }))
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
    show = None
    if "show" in request.GET:
        show = request.GET.get('show')
    inteventsIDList = []
    form = bg_registration_form()
    if request.method == "POST":
        form = bg_registration_form(request.POST)
        event_name = ""
        how_heard = None
        eventsIDList = request.POST.getlist('eventsCheck')
        how_heard = request.POST.get('how_heard')
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
                message = "Thank you for registering with Bay Area Wedding Fairs.<br /><br />%s<br /><br />If you like to save time and money, pre-pay online at <a href='https://bayareaweddingfairs.com/bride-groom-registration/'>https://bayareaweddingfairs.com/bride-groom-registration/</a>. Also, we encourage you to go to our <a href='https://www.facebook.com/baweddingfairs/events'>Facebook Events Page</a>, select the Fair and click on 'Join'. You will be entered in our weekly 'Las Vegas Giveaway' drawing (Winner will be announced on our Facebook page). <br /><br />NEED HELP IN PLANNING? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />if you have any questions, please email us at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com </a><br /><br />We look forward to seeing you at the Wedding Fair<br /><br />Thank You!<br /><br />Bay Area Wedding Fairs" % (
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
    try:
        inteventsIDList.append(int(show))
    except Exception as e:
        print e

    content = {
        'form': form,
        'events': events,
        'error_message': error_message,
        'eventsIDList': eventsIDList,
        'inteventsIDList': inteventsIDList,
        'eventsCheck': eventsCheck,
        'all_events': events,
        'how_heard': how_heard,
        'show': show,
    }
    return render(request, "bayareaweddingfairs/site/BGRegister/BGRegister.html", content)

def VendorRegistrationIndex(request):
    return HttpResponse('Awaiting')

@csrf_exempt
def BrideGroomTicket(request):
    event = None
    hide_thanks = request.GET.get('nothanks')
    """
    Needs to be converted to Live keys via
    settings.STRIPE_SECRET_KEY_BAWF
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
    ticketform = CreditCardBAWFTicketForm()
    valid_code = ""
    error_message = ""
    amount = 0
    promo_code_discount = None
    if request.method == 'POST':
        ticketform = CreditCardBAWFTicketForm(request.POST or None)
        if ticketform.is_valid():
            email = ticketform.cleaned_data.get('email')
            event = request.POST.get('event')
            phone = ticketform.cleaned_data.get('phone')
            month = ticketform.cleaned_data.get('month')
            year = ticketform.cleaned_data.get('year')
            stripe_token = request.POST.get('stripe_token')
            promocode = request.POST.get('promocode')
            quantity_tickets = request.POST.get('quantityTickets')
            earlybird_ticket = request.POST.get('earlybirdTickets')
            group_ticket = request.POST.get('groupTickets')
            event_date = request.POST.get('event_date')
            event = Event_fairs.objects.get(id=event)
            group = 0
            easybird = 0
            # if str(event_date) == str(datetime.now().date().strftime('%b. %d, %Y')):
            #     amount = float(event.amount) * float(int(quantity_tickets))
            # else:
            #     amount = 0
            normal_tickets = float(event.amount) * float(int(quantity_tickets))
            easybird = (float(event.earlybird_ticket) * float(int(earlybird_ticket)))
            group = float(event.group_ticket) * float(int(group_ticket))
            amount = normal_tickets + easybird + group
            try:
                promo_code_discount = Promocode.objects.get(code=promocode)
                if promo_code_discount.is_Available:
                    if promo_code_discount.type == Promocode.AMOUNT:
                        tickets_price = float(event.amount) - float(promo_code_discount.amount_percent)
                        new_earlyBirdPrice = float(event.earlybird_ticket) - float(promo_code_discount.amount_percent)
                        new_groupPrice = float(event.group_ticket) #- float(promo_code_discount.amount_percent)
                        amount = float(new_groupPrice) * int(group_ticket) + float(new_earlyBirdPrice) * int(
                            earlybird_ticket) + float(tickets_price) * int(quantity_tickets)

                    elif promo_code_discount.type == Promocode.PERCENT:
                        tickets_price = (float(event.amount) /100) * float(promo_code_discount.amount_percent)
                        new_earlyBirdPrice = (float(event.earlybird_ticket) /100) * float(promo_code_discount.amount_percent)
                        new_groupPrice = float(event.group_ticket)  # - float(promo_code_discount.amount_percent)
                        amount = float(new_groupPrice) * int(group_ticket) + float(new_earlyBirdPrice) * int(
                            earlybird_ticket) + float(tickets_price) * int(quantity_tickets)
            except Exception as e:
                print e
            amount = int(amount * 100)
            charge = None
            if stripe_token:
                charge = stripe.Charge.create(
                    amount=amount,  # amount in cents, again
                    currency="usd",
                    source=stripe_token,
                    description="Ticket purchased by %s, quatity: %s, amount: %s" % (email, quantity_tickets, amount)
                )
            # try:
            if charge:
                code = id_generator()
                qr = pyqrcode.create(code)
                filename = '{}'.format((datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
                filename = filename + '.png'
                qr.png(filename, scale=7)
                image_link = save_to_S3(filename)
                ticket = EventTickets()
                ticket.event = event
                ticket.email = email
                ticket.phone = phone
                ticket.card = charge.stripe_id
                ticket.amount = amount
                ticket.quantity = quantity_tickets
                ticket.earlybird_ticket = earlybird_ticket
                ticket.group_ticket = group_ticket
                ticket.code = code
                ticket.path_upload = image_link
                if promo_code_discount:
                    ticket.promocode_success = promo_code_discount
                ticket.save()
                result = send_email_ticket_bawf(sender="info@bayareaweddingfairs.com",
                                                subject="Bay Area Wedding Fairs: Ticket",
                                                receive=email,
                                                title="Thank you for purchasing Bay Area Wedding Fairs Tickets",
                                                message='Your ticket reservation has been made against the following show: <br /><br />- %s<br /><br />Quantity of Standard tickets: %s<br />Quantity of EarlyBirds Discounted tickets: %s<br />Quantity of Group Discounted tickets: %s<br />Total amount processed: $%s<br />Promotion code (if any): %s<br /><br />We are looking forward to have you in the show, feel free to contact for any queries info@bayareaweddingfairs.com' % (
                                                    event, ticket.quantity, ticket.earlybird_ticket,
                                                    ticket.group_ticket,
                                                    int(ticket.amount / 100), ticket.promocode_success),
                                                object=ticket, link=image_link)
                tickets_sold_total = EventTickets.objects.filter(event=event)
                normal = 0
                early_normal = 0
                group_normal = 0
                for o in tickets_sold_total:
                    normal += int(o.quantity)
                    early_normal += int(o.earlybird_ticket)
                    group_normal += int(o.group_ticket)
                total_tickets_sold = normal+early_normal+group_normal
                send_email_ticket_bawf_ticket(sender="info@bayareaweddingfairs.com",
                                                subject="Bay Area Wedding Fairs: Ticket Summary",
                                                receive=['adeelpkpk@gmail.com','info@bayareaweddingfairs.com'],
                                                message='<b>ORDER DETAILS<br/><br/>Time: %s<br />Order ID: %s<br />Tickets Sold: %s<br />Amount: %s<br />Tracking Code: %s<br />Buyer: %s<br />Buyer Phone: %s<br /><hr />Event: %s<br />Venue: %s<br />Event Date: %s<br />Sales: You have now sold %s tickets for this date' % (
                                                    str(datetime.now()),
                                                    ticket.id,
                                                    ticket.get_all_tickets(),
                                                    ticket.get_amount(),
                                                    ticket.code,
                                                    ticket.email,
                                                    ticket.phone,
                                                    str(ticket.event.name),
                                                    str(ticket.event.location),
                                                    str(ticket.event.date),
                                                    total_tickets_sold
                                                ))
                return render(request, "bayareaweddingfairs/site/BGTicket/Success.html", {
                    'object': ticket,
                })
            # except Exception as e:
            #     print "exceptionBuyTickets: ", e
        else:
            print "form not valid"
    """
        Needs to be converted to Live keys via
        settings.STRIPE_PUBLISHABLE_KEY_BAWF
    """
    context = {
        'pub_key': settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'event': Event_fairs.objects.filter(date__gte=datetime.now().date()).filter(amount__isnull=False).filter(Q(standard_ticket_visible=True)|Q(earlybird_ticket_visible=True)|Q(group_ticket_visible=True)).exclude(id__in=[46,47,48,49,50,51,52]).order_by('date'),
        'form': ticketform,
        'hide_thanks': hide_thanks,
    }
    return render(request, "bayareaweddingfairs/site/BGTicket/BGTicket.html", context)

"""Local Settings """
conn = boto.connect_s3(
        aws_access_key_id='AKIAIXFGL3W7R47QWV2A',
        aws_secret_access_key='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',
    )
# conn = boto.connect_s3(
#         aws_access_key_id=AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     )
bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
import sys


def save_to_S3(file_name):

    key_name = file_name
    path = '/static/images/bawf/'
    full_key_name = os.path.join(path, key_name)
    k = bucket.new_key(full_key_name)
    k.set_contents_from_filename(key_name, cb=percent_cb, num_cb=10)
    link_ = 'https://bayareaweddingfairs-static.s3.amazonaws.com/static/images/bawf/' + file_name

    print "link: ", link_
    os.remove(file_name)
    return link_


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


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

def BrideGroomTicketSuccess(request):
    return render(request, "bayareaweddingfairs/site/BGTicket/Success.html")

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


def eventDetail(request, id):
    event_dict = {}
    event = Event_fairs.objects.get(id=id)
    print "event: " , event.amount
    event_dict = {
        'standard_price': event.amount,
        'standard_ticket_name': event.standard_ticket_name,
        'standard_ticket_visible': event.standard_ticket_visible,
        'earlybird_ticket': event.earlybird_ticket,
        'earlybird_ticket_name': event.earlybird_ticket_name,
        'earlybird_ticket_visible': event.earlybird_ticket_visible,
        'group_ticket': event.group_ticket,
        'group_ticket_name': event.group_ticket_name,
        'group_ticket_visible': event.group_ticket_visible


    }

    return HttpResponse(json.dumps( event_dict))
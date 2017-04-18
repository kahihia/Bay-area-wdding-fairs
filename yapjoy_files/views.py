from django.shortcuts import render, HttpResponseRedirect, Http404, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from yapjoy_registration.models import UserProfile, User
from yapjoy_registration.commons import id_generator
from yapjoy_registration.views import send_email
from django.http import JsonResponse
from yapjoy.settings import MEDIA_URL
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.core.urlresolvers import reverse
from bayareaweddingfairs_tickets.models import *
from bayareaweddingfairs_tickets.views import send_email_ticket_bawf
from django.template.loader import render_to_string
from django.contrib.auth.decorators import user_passes_test
import pyqrcode
import boto
from django.db.models import F, FloatField, Sum

from django.db.models import Sum

@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def crm(request):
    user = request.user
    WpForm = WpInfoForm()
    events = HostEvent.objects.all()
    userinfos = UserInfo.objects.all()
    event_name = ""

    if "emails" in request.POST:
        emails = request.POST.get('emails')
        print 'email',emails
        emails = emails.split(',')
        code = id_generator()

        for email in emails:
            print "Sending email to: ", email.strip()
            try:
                send_email(email, message="You have been invited by %s.<br/><br/>If you want to accept invitation,then kindly click link below.<br /><br /><a href='https://dev.yapjoy.com/>ACCEPT</a>"%(user.get_full_name()), title="Wedding Professional %s"%(user.get_full_name()), subject="Wedding Professional Invitation")
                print 'email is sent'
            except:
                pass

    if user.userprofile.type == UserProfile.PROFESSIONAL and not user.is_superuser:
        print "not superuser but wp"
        try:
            wpinfo = WpInfo.objects.get(email=user.email)
            initial = {
                'firstname':wpinfo.firstname,
                'lastname':wpinfo.lastname,
                'email':wpinfo.email,
                'date':wpinfo.date,
                'amount':wpinfo.amount,
            }
            WpForm = WpInfoForm(initial=initial)
            event_name = wpinfo.event.subject
            print "have form"

        except:
            WpForm = []
            wpinfo = []
            event_name = ''

        if "wpForm" in request.POST:
            wpinfoForm = WpInfoForm(request.POST)
            print wpinfoForm

            if wpinfoForm.is_valid():
                accept = wpinfoForm.cleaned_data['accept']

                if accept == True:
                    try:
                        wpinfo.accepted = True
                        wpinfo.save()
                        feedback = "success"

                    except:
                        feedback = "fail"
                else:
                    feedback = "not accepted"
            else:
                feedback = "not valid"

            content = {
                'feedback': feedback
            }

            return HttpResponseRedirect("/crm/")
            # return JsonResponse(content, safe=False)

        # print WpForm
        # content = {
        #     'userinfos':userinfos,
        #     'events': events,
        #     'WpForm': wpForm,
        # }
        #
        # template_name = 'vendroid/CRM/home.html'
        # return render(request, template_name, content)


    elif request.method == "POST" and user.is_superuser:
        # elif "wpForm" in request.method == "POST":
        #if "wpForm" in request.POST:
        print 'inside wp form'
        wpinfoForm = WpInfoForm(request.POST)
        print wpinfoForm

        if wpinfoForm.is_valid():
            print "get into form"
            firstname = wpinfoForm.cleaned_data['firstname']
            lastname = wpinfoForm.cleaned_data['lastname']
            date = wpinfoForm.cleaned_data['date']
            # event_id = wpinfoForm.cleaned_data['event']
            email = wpinfoForm.cleaned_data['email']
            amount = wpinfoForm.cleaned_data['amount']

            #deal with event
            event_id = request.POST.get('events_to')
            # print "event_id "+str(event_id)

            try:
                event = HostEvent.objects.get(id=event_id)
            except:
                event = []

            print "email is "+str(email)

            try:
                wp = WpInfo.objects.get(email=email)
                # feedback = "fail"
                print "already exist wp email "+str(email)

            except:
                wp = WpInfo.objects.create(firstname=firstname,
                                           lastname=lastname,
                                           date=date,
                                           event=event,
                                           email=email,
                                           amount=amount)
                # feedback = "success"
                print "created wp model "+str(email)

            return HttpResponseRedirect("/crm/")
        else:
            print "form not valid"
            messages.error(request, "form submission failed")


    #Can select specific csvfile's userinfo in the future----fix me
    # print "Email is "+str(userinfos[0].Email)
    content = {
        'userinfos':userinfos,
        'events': events,
        'WpForm': WpForm,
        'event_name': event_name,
    }

    template_name = 'vendroid/CRM/home.html'
    return render(request, template_name, content)

@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def event_management(request):
    user = request.user
    profile = user.userprofile
    form = registration_event_form()
    if request.method == "POST":
        form = registration_event_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            print request.POST.getlist('id_event')
    events = Event_fairs.objects.filter(Q(is_expired=False)& ~Q(name="Las Vegas GiveAway"))

    content = {
        'form':form,
        'events ':events,
    }

    template_name = 'vendroid/CRM/events.html'
    return render(request, template_name, content)

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
import string
import random
import json
from yapjoy_registration.commons import id_generator
@login_required(login_url='/login/')
@staff_member_required
def invoice_add(request, id):
    user = request.user
    successMessage = None
    invoice = Register_Event.objects.get(id=id)
    form = InvoiceCreationForm(initial={'is_sent':True,
                                        })
    if request.method == "POST":
        form = InvoiceCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            amount = data['amount']
            notes = data['notes']
            prize = data['prize']
            is_sent = data['is_sent']
            code = id_generator()
            invoice_event = Invoice_Event.objects.create(registered_event=invoice,
                                                         user=user,
                                                         amount=amount,
                                                         prize=prize,
                                                         notes=notes,
                                                         code=code,
                                                         is_sent=is_sent)
            if is_sent:
                context = {
                    'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(invoice_event.code),
                    'title':"Bay Area Wedding Fairs Invoice",
                    }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [invoice_event.registered_event.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                successMessage = "Invoice request sent successfully."
            else:
                successMessage = "Invoice is created successfully, but is not sent."
    return render(request, 'vendroid/CRM/create_invoice.html',{
        'form':form,
        'id':id,
        'invoice':invoice,
        'successMessage':successMessage,
    })

from yapjoy_registration.models import Company
@login_required(login_url='/crm/login/')
@staff_member_required
@csrf_exempt
def event_management(request):
    user = request.user
    profile = user.userprofile
    # initial = {
    #     'name':'%s'%(user.get_full_name()),
    #     'phone':profile.phone,
    #     'email':user.email,
    #     'city':profile.city,
    #     'zip':profile.zip,
    #     'business_name':profile.userprofile_company.name,
    # }
    error_message = None
    form = registration_event_form()


    if request.method == "POST":
        print "inside post"
        form = registration_event_form(request.POST)
        if form.is_valid():
            print 'form is valid'
            data = form.cleaned_data

            print data
            eventsIDList = request.POST.getlist('eventsCheck')
            if eventsIDList:
                # for e in events:
                #     try:
                #         eventget = request.POST.get('id_event_'+e.id)
                #     except:
                #         eventget = ""
                #         print "get none", 'id_event_'+e.id, e.name, e.date
                #
                #     print eventget

                name = data['name']
                business_name = data['business_name']
                phone = data['phone']
                email = data['email']
                city = data['city']
                zip = data['zip']
                comments = data['comments']
                how_heard = data['how_heard']
                category = data['category']
                # event = data['event']

                print category, how_heard
                user_reg = None
                try:
                    user_reg = User.objects.get(email=email, username=email)
                except:
                    user_reg = User.objects.create(email=email, username=email)
                    profile = UserProfile.objects.get(user=user_reg)
                    profile.type = UserProfile.PROFESSIONAL
                    profile.save()
                    company = Company.objects.create(userprofile=profile, name=business_name)

                for eID in eventsIDList:
                    event = Event_fairs.objects.get(id=eID)
                    print event.name, event.date
                    try:
                        regs = Register_Event.objects.filter(event=event, email=user_reg.email)
                        reg = regs[0]
                        reg.user=user_reg,
                        reg.name=name,
                        reg.buser.usiness_name=business_name,
                        reg.phone=phone,
                        reg.email=user_reg.email,
                        reg.city=city,
                        reg.zip=zip,
                        reg.comments=comments,
                        reg.how_heard=how_heard,
                        reg.category=category,
                        reg.event=event,
                        reg.type=Register_Event.BGUSER,
                        reg.save()
                    except:
                        reg = Register_Event.objects.create(
                                                            user=user_reg,
                                                            name=name,
                                                            business_name=business_name,
                                                            phone=phone,
                                                            email=user_reg.email,
                                                            city=city,
                                                            zip=zip,
                                                            comments=comments,
                                                            how_heard=how_heard,
                                                            category=category,
                                                            event=event,
                                                            type=Register_Event.BGUSER,
                                                            )


                # Invoice_Event.objects.create(registered_event=reg, user=user)
                print 'created'
                return HttpResponseRedirect('/crm/invoices/')
            else:
                error_message = "Select an event atleast"


    #coverging events by season
    events = Event_fairs.objects.filter(Q(is_expired=False)& ~Q(name="Las Vegas GiveAway"))

    spring_events = []
    summer_events = []
    fall_events = []
    winter_events = []
    for event in events:
        season = choose_season(event)
        # print event.name, event.date, event.date.month, season

        if season == 'Spring':
            spring_events.append(event)
        elif season == 'Summer':
            summer_events.append(event)
        elif season == 'Fall':
            fall_events.append(event)
        elif season == 'Winter':
            winter_events.append(event)
        else:
            print "Season is wrong", event.date

    content = {
        'form':form,
        'events':events,
        'spring_events': spring_events,
        'summer_events':summer_events,
        'fall_events':fall_events,
        'winter_events':winter_events,
        'error_message':error_message,

    }

    template_name = 'vendroid/CRM/events.html'
    return render(request, template_name, content)


# @login_required(login_url='/login/')
# @staff_member_required
# @csrf_exempt
def event_management_iframe_success(request):
    return render(request, 'vendroid/CRM/event_success_iframe.html')

def event_management_iframe_bg_success(request):
    # print code
    return render(request, 'vendroid/CRM/event_success_iframe_bg.html')

def event_register_iframe_bg_success(request):
    return render(request, 'vendroid/CRM/register_success_iframe_bg.html')

@csrf_exempt
def event_management_iframe_bg_successv2(request, id):
    print id
    event = None
    # secret_key = 'sk_test_enH3Di38sTWreGlOZPBNML93'
    # pub_key = 'pk_test_tZdpLY6bm1aDvhy9tBdfyMeV'
    stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
    # global promocode_code
    # event = Event_fairs.objects.get(id=id)
    ticketform = CreditCardBAWFTicketForm(initial={
        'email': 'adeelpkpk@gmail.com',
        'number': '4242424242424242',
        'year': '2017',
        'phone': '2017'
    })
    print "in the but ticket"
    valid_code = ""
    error_message = ""
    amount = 0
    promo_code_discount = None
    if request.method == 'POST':
        ticketform = CreditCardBAWFTicketForm(request.POST or None)
        if ticketform.is_valid():
            print 'form'
            email = ticketform.cleaned_data.get('email')
            event = request.POST.get('event')
            phone = ticketform.cleaned_data.get('phone')
            month = ticketform.cleaned_data.get('month')
            year = ticketform.cleaned_data.get('year')
            stripe_token = request.POST.get('stripe_token')
            promocode = request.POST.get('promocode')
            quantity_tickets = request.POST.get('quantityTickets')
            print quantity_tickets
            event = Event_fairs.objects.get(id=event)
            amount = float(event.amount) * float(int(quantity_tickets))

            try:
                promo_code_discount = Promocode.objects.get(code=promocode)
                if promo_code_discount.is_Available:
                    if promo_code_discount.type == Promocode.AMOUNT:
                        amount -= float(promo_code_discount.amount_percent)
                    elif promo_code_discount.type == Promocode.PERCENT:
                        amount = (amount / 100) * float(Promocode.amount_percent)
            except Exception as e:
                print e
            amount = int(amount * 100)
            print "Amount in cents: ", amount
            charge = None
            if stripe_token:
                charge = stripe.Charge.create(
                    amount=amount,  # amount in cents, again
                    currency="usd",
                    source=stripe_token,
                    description="Ticket purchased by %s, quatity: %s, amount: %s" % (email, quantity_tickets, amount)
                )
                print charge
            print "data: ", phone, month, year, quantity_tickets, stripe_token, email, event, promocode, amount

            # expire = str(month)+"/"+str(year)
            try:
                if charge:
                    # if promocode_code:
                    #     valid_code = Promocode.objects.get(code=promocode_code)
                    # else:
                    #     promocode_code = ""
                    print "event: ",
                    ticket = EventTickets()

                    ticket.event = event
                    ticket.email = email
                    ticket.phone = phone
                    # ticket.card = number
                    ticket.amount = amount
                    # ticket.expire = expire
                    ticket.quantity = quantity_tickets
                    code = id_generator()
                    print "code: ", code
                    ticket.code = code
                    if promo_code_discount:
                        print "valid"
                        ticket.promocode_success = promo_code_discount
                        # else:

                        # ticket.promocode_success = ""
                        # print "ticket"
                    ticket.save()
                    print "ticket: saved"
                    result = send_email_bawf(sender="info@bayareaweddingfairs.com", subject="Bay Area Wedding Fairs: Ticket",
                                             receive=email,
                                             title="Thank you for purchasing Bay Area Wedding Fairs Tickets",
                                             message='Your ticket reservation has been made against the following show: <br /><br />- %s<br /><br />Quantity of online tickets: %s<br />Total amount processed: $%s<br />Promotion code (if any): %s<br /><br />We are looking forward to have you in the show, feel free to contact for any queries info@bayareaweddingfairs.com' %(event,ticket.quantity,int(ticket.amount/100), ticket.promocode_success ))
                    # if result == True:
                    return render(request, "vendroid/bayareaweddingfairs_tickets/thankyou_page.html", )
            except Exception as e:
                print "exceptionBuyTickets: ", e.message

        else:
            print "form not valid"
    context = {
        'pub_key': settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'event': Event_fairs.objects.filter(date__gte=datetime.now().date()).filter(amount__isnull=False).order_by('date'),
        'form': ticketform
    }

    # return render(request, 'vendroid/bayareaweddingfairs_tickets/buy_tickets.html', context)
    return render(request, 'vendroid/CRM/event_success_iframe_bg.html', context=context)

@csrf_exempt
def event_management_iframe_bg_successv2(request):
    event = None
    hide_thanks = request.GET.get('nothanks')
    """
    Needs to be converted to Live keys via
    settings.STRIPE_SECRET_KEY_BAWF
    """
    stripe.api_key = 'sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt'
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
            if str(event_date) == str(datetime.now().date().strftime('%b. %d, %Y')):
                amount = float(event.amount) * float(int(quantity_tickets))
            else:
                amount = 0
            easybird = (float(event.earlybird_ticket) * float(int(earlybird_ticket)))
            group = float(event.group_ticket) * float(int(group_ticket))
            amount = amount + easybird + group
            try:
                promo_code_discount = Promocode.objects.get(code=promocode)
                if promo_code_discount.is_Available:
                    if promo_code_discount.type == Promocode.AMOUNT:
                        new_earlyBirdPrice = float(event.earlybird_ticket) - float(promo_code_discount.amount_percent)
                        new_groupPrice = float(event.group_ticket) - float(promo_code_discount.amount_percent)
                        amount = float(new_groupPrice) * int(group_ticket) + float(new_earlyBirdPrice) * int(earlybird_ticket)

                    elif promo_code_discount.type == Promocode.PERCENT:
                        amount = (amount / 100) * float(promo_code_discount.amount_percent)
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
            try:
                if charge:
                    print "event: ",
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
                    result = send_email_ticket_bawf(sender="info@bayareaweddingfairs.com", subject="Bay Area Wedding Fairs: Ticket",
                                             receive=email,
                                             title="Thank you for purchasing Bay Area Wedding Fairs Tickets",
                                             message='Your ticket reservation has been made against the following show: <br /><br />- %s<br /><br />Quantity of Standard tickets: %s<br />Quantity of EarlyBirds Discounted tickets: %s<br />Quantity of Group Discounted tickets: %s<br />Total amount processed: $%s<br />Promotion code (if any): %s<br /><br />We are looking forward to have you in the show, feel free to contact for any queries info@bayareaweddingfairs.com' % (
                                             event, ticket.quantity, ticket.earlybird_ticket, ticket.group_ticket,
                                             int(ticket.amount / 100), ticket.promocode_success), object=ticket,  link=image_link)
                    return render(request, "vendroid/bayareaweddingfairs_tickets/thankyou_page.html",{
                        'object':ticket,
                    } )
            except Exception as e:
                print "exceptionBuyTickets: ", e.message
        else:
            print "form not valid"
    """
        Needs to be converted to Live keys via
        settings.STRIPE_PUBLISHABLE_KEY_BAWF
    """
    context = {
        'pub_key': 'pk_test_ic11SWVPcUHwZ1mDBEBTdSX1',
        'event': Event_fairs.objects.filter(date__gte=datetime.now().date()).filter(amount__isnull=False).exclude(id__in=[46,47,48,49,50,51,52]).order_by('date'),
        'form': ticketform,
        'hide_thanks': hide_thanks,
    }
    return render(request, 'vendroid/CRM/event_success_iframe_bgv2.html', context=context)


@csrf_exempt
def event_management_iframe(request):

    is_completed = None
    error_message = None
    eventsIDList = None
    inteventsIDList = None
    eventsCheck = None
    how_heard = None
    form = registration_event_form()

    if request.method == "POST":
        print "inside post"
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
            print 'form is valid'
            data = form.cleaned_data

            print data

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
                # event = data['event']

                print category, how_heard
                user_reg = None
                try:
                    user_reg = User.objects.get(email__iexact=email)
                except:
                    user_reg = User.objects.create(email=email, username=email)
                    profile = UserProfile.objects.get(user=user_reg)
                    profile.type = UserProfile.PROFESSIONAL
                    profile.save()
                    company = Company.objects.create(userprofile=profile, name=business_name)
                event_name = ""

                # admin_user = User.objects.get(username__iexact="administrator")
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
                                                        # event=event,
                                                        # sales=admin_user,
                                                        type=Register_Event.CONTRACTOR,
                                                        website=website,
                                                        )
                for eID in eventsIDList:
                    event = Event_fairs.objects.get(id=eID)
                    print event.name, event.date
                    reg.event.add(event)
                    # try:
                    #     regs = Register_Event.objects.filter(event=event, email=user_reg.email)
                    #     reg = regs[0]
                    #     reg.user=admin_user,
                    #     reg.name=name,
                    #     reg.buser.usiness_name=business_name,
                    #     reg.phone=phone,
                    #     reg.email=user_reg.email,
                    #     reg.city=city,
                    #     reg.zip=zip,
                    #     reg.comments=comments,
                    #     reg.how_heard=how_heard,
                    #     reg.category=category,
                    #     reg.event=event,
                    #     reg.type=Register_Event.BGUSER,
                    #     reg.save()
                    # except:



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
                # Invoice_Event.objects.create(registered_event=reg, user=user)
                print 'created'
                message = "Thank you for registering with Bay Area Wedding Fairs. We will get back to you soon.<br /><br />LOOKING FOR MORE WEDDING BUSINESS?? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />If you have any questions, please email us directly at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com</a><br /><br />Thank You!<br /><br />Bay Area Wedding Fairs"
                send_bawf_email(sendTo=user_reg.email, message=message, title="", subject="Registration Successful!")
                is_completed = True
                # return HttpResponseRedirect('/crm/invoices/addition/success/iframe/')
            else:
                error_message = "Select an event atleast"


    #coverging events by season
    events = Event_fairs.objects.filter(Q(is_expired=False)&Q(date__gte=datetime.now())).order_by('date')
    # spring_events = []
    # summer_events = []
    # fall_events = []
    # winter_events = []
    # for event in events:
    #     season = choose_season(event)
    #     # print event.name, event.date, event.date.month, season
    #
    #     if season == 'Spring':
    #         spring_events.append(event)
    #     elif season == 'Summer':
    #         summer_events.append(event)
    #     elif season == 'Fall':
    #         fall_events.append(event)
    #     elif season == 'Winter':
    #         winter_events.append(event)
    #     else:
    #         print "Season is wrong", event.date

    content = {
        'form':form,
        'events':events,
        # 'spring_events': spring_events,
        # 'summer_events':summer_events,
        # 'fall_events':fall_events,
        # 'winter_events':winter_events,
        'error_message':error_message,
        'eventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'is_completed':is_completed,
        'how_heard':how_heard,

    }

    template_name = 'vendroid/CRM/events_iframe.html'
    return render(request, 'vendroid/CRM/events_iframe.html', content)




@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def event_management_iframe_local(request):
    # user = request.user
    # profile = user.userprofile
    # initial = {
    #     'name':'%s'%(user.get_full_name()),
    #     'phone':profile.phone,
    #     'email':user.email,
    #     'city':profile.city,
    #     'zip':profile.zip,
    #     'business_name':profile.userprofile_company.name,
    # }
    is_completed = None
    error_message = None
    eventsIDList = None
    inteventsIDList = None
    eventsCheck = None
    how_heard = None
    form = registration_event_form()


    if request.method == "POST":
        print "inside post"
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
            print 'form is valid'
            data = form.cleaned_data

            print data

            if eventsIDList:
                # for e in events:
                #     try:
                #         eventget = request.POST.get('id_event_'+e.id)
                #     except:
                #         eventget = ""
                #         print "get none", 'id_event_'+e.id, e.name, e.date
                #
                #     print eventget

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
                # event = data['event']

                print category, how_heard
                user_reg = None
                try:
                    user_reg = User.objects.get(email__iexact=email)
                except:
                    user_reg = User.objects.create(email=email, username=email)
                    profile = UserProfile.objects.get(user=user_reg)
                    profile.type = UserProfile.PROFESSIONAL
                    profile.save()
                    company = Company.objects.create(userprofile=profile, name=business_name)
                event_name = ""

                # admin_user = User.objects.get(username__iexact="administrator")
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
                                                        # event=event,
                                                        type=Register_Event.CONTRACTOR,
                                                        website=website,
                                                        )
                for eID in eventsIDList:
                    event = Event_fairs.objects.get(id=eID)
                    print event.name, event.date
                    reg.event.add(event)
                    # try:
                    #     regs = Register_Event.objects.filter(event=event, email=user_reg.email)
                    #     reg = regs[0]
                    #     reg.user=admin_user,
                    #     reg.name=name,
                    #     reg.buser.usiness_name=business_name,
                    #     reg.phone=phone,
                    #     reg.email=user_reg.email,
                    #     reg.city=city,
                    #     reg.zip=zip,
                    #     reg.comments=comments,
                    #     reg.how_heard=how_heard,
                    #     reg.category=category,
                    #     reg.event=event,
                    #     reg.type=Register_Event.BGUSER,
                    #     reg.save()
                    # except:



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
                        <b>Comments</b> : %s"""%(name, user_reg.email, phone, city, zip, category, business_name, event_name, how_heard, comments)
                send_bawf_email(sendTo="info@bayareaweddingfairs.com", message=message2, title="Registered Vendor Information:", subject="A NEW VENDOR HAS REGISTERED")
                # Invoice_Event.objects.create(registered_event=reg, user=user)
                print 'created'
                # message = "Thank you for registering with Bay Area Wedding Fairs. We will get back to you soon.<br /><br />LOOKING FOR MORE WEDDING BUSINESS?? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />If you have any questions, please email us directly at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com</a><br /><br />Thank You!<br /><br />Bay Area Wedding Fairs"
                # send_bawf_email(sendTo=user_reg.email, message=message, title="", subject="Registration Successful!")
                is_completed = True
                form = registration_event_form()
                # return HttpResponseRedirect('/crm/invoices/addition/success/iframe/')
            else:
                error_message = "Select an event atleast"


    #coverging events by season
    events = Event_fairs.objects.filter(Q(Q(date__gte=datetime.now())& ~Q(name="Las Vegas GiveAway"))|Q(id=42))
    # spring_events = []
    # summer_events = []
    # fall_events = []
    # winter_events = []
    # for event in events:
    #     season = choose_season(event)
    #     # print event.name, event.date, event.date.month, season
    #
    #     if season == 'Spring':
    #         spring_events.append(event)
    #     elif season == 'Summer':
    #         summer_events.append(event)
    #     elif season == 'Fall':
    #         fall_events.append(event)
    #     elif season == 'Winter':
    #         winter_events.append(event)
    #     else:
    #         print "Season is wrong", event.date

    content = {
        'form':form,
        'events':events,
        # 'spring_events': spring_events,
        # 'summer_events':summer_events,
        # 'fall_events':fall_events,
        # 'winter_events':winter_events,
        'error_message':error_message,
        'eventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'is_completed':is_completed,
        'how_heard': how_heard,

    }

    # template_name = 'vendroid/CRM/events_iframe_local.html'
    return render(request, 'vendroid/CRM/events_iframe_local.html', content)




def choose_season(event):
    # season_dict = collections.defaultdict(list)
    # season_dict = {'Spring': ['March', 'April', 'May'],
    #                'Summer': ['Jun', 'July', 'Aug'],
    #                'Fall': ['Sep', 'Oct', 'Nov'],
    #                'Winter': ['Dec', 'Jon', 'Feb']}

    season_dict = {'Spring': [3, 4, 5],
                   'Summer': [6, 7, 8],
                   'Fall': [9, 10, 11],
                   'Winter': [12, 1, 2]}

    month = int(event.date.month)
    # print event.name, event.date, month
    for k in season_dict:
        if month in season_dict[k]:
            # event.season = k
            # event.save()
            return k

    return ""
    # event.season = [k if month in season_dict[k] else "" for k in season_dict ]


@login_required(login_url="/login/")
@staff_member_required
def event_invoice(request):
    user = request.user
    events = Register_Event.objects.all()
    print events
    invoice_id = None
    try:
        invoice_id = request.GET['invoice_id']
    except:
        pass
    return render(request, 'vendroid/CRM/invoices.html', {
        'events':events,
        'invoice_id':invoice_id,
    })

@login_required(login_url="/login/")
@staff_member_required
def media_kit(request):

    user = request.user
    successMessage = None
    media_kits = None
    initial = {
        "special_instructions_one":"Levi's(r) Stadium & Fairmont shows are priced $200 higher as they are our premium shows.",
    }
    form = MediaKitForm(initial=initial)
    if user.is_superuser:
        media_kits = MediaKit.objects.all().select_related('user').order_by('-created_at')
    elif user.is_staff:
        media_kits = MediaKit.objects.filter(user=user).select_related('user').order_by('-created_at')
    if 'search' in request.POST:
        search = request.POST.get('search')
        media_kits = media_kits.filter(
            Q(user__email__icontains=search)|Q(user__username__icontains=search)|Q(vendor_name__icontains=search)|Q(email__icontains=search)).order_by('-created_at')
    elif request.method == 'POST':
        form = MediaKitForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            vendor_name = data['vendor_name']
            business_name = data['business_name']
            business_category = data['business_category']
            email = data['email']
            session = data['session']
            booth_offered = data['booth_offered']
            normal_price = data['normal_price']
            one_show_price = data['one_show_price']
            two_show_price = data['two_show_price']
            three_show_price = data['three_show_price']
            prize_value = data['prize_value']
            special_instructions_one = data['special_instructions_one']
            special_instructions_two = data['special_instructions_two']
            special_instructions_three = data['special_instructions_three']
            opening_remarks = data['opening_remarks']
            m_kit = MediaKit.objects.create(user=user,
                                    vendor_name=vendor_name,
                                    business_name=business_name,
                                    business_category=business_category,
                                    email=email,
                                    session=session,
                                    booth_offered=booth_offered,
                                    normal_price=normal_price,
                                    one_show_price=one_show_price,
                                    two_show_price=two_show_price,
                                    three_show_price=three_show_price,
                                    prize_value=prize_value,
                                    special_instructions_one=special_instructions_one,
                                    special_instructions_two=special_instructions_two,
                                    special_instructions_three=special_instructions_three,
                                    opening_remarks=opening_remarks
                                    )
            context = {
                'message': "Dear %s, we have created a media kit, specially customized for you. <br /><br />Click on the following link to view it. My contact information is listed on the media kit. Please feel free to contact me with any questions. I will be following up with you in a few days.<br /><br /><a href='https://www.yapjoy.com/crm/mediakit/view/%s' target='_blank' class='btn'>Open Media Kit</a>" % (m_kit.vendor_name,
                m_kit.code),
                'title': "Bay Area Wedding Fairs - Requested Media Kit",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("Bay Area Wedding Fairs Media Kit You Requested", text_content, "%s <%s>"%(user.get_full_name(), user.email),
                                         ["%s <%s>"%(m_kit.vendor_name, m_kit.email)], bcc=[user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # print 'code: ',m_kit.code, m_kit.status
            successMessage = "Message has been sent successfully."
    return render(request, 'vendroid/CRM/mediakit.html', {
        'form':form,
        'user':user,
        'media_kits':media_kits,
       # 'successMessage':successMessage,
    })

# @login_required(login_url="/login/")
# @staff_member_required
def media_kit_view(request, code):
    media_kit = get_object_or_404(MediaKit, code=code)
    if media_kit.status == MediaKit.PENDING:
        context = {
            'message': "The Media Kit has been viewed by %s of %s" % (
                media_kit.vendor_name, media_kit.business_name),
            'title': "Bay Area Wedding Fairs - MediaKit Viewed",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs - MediaKit Viewed", text_content, 'info@bayareaweddingfairs.com',
                                    [media_kit.user.email] )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        media_kit.status = MediaKit.VIEWED
        media_kit.viewed = datetime.now()
        media_kit.save()
    return render(request, 'vendroid/CRM/mediaKitTemplateV2.html', {
        'media_kit':media_kit,
    })


def media_kit_viewv2(request, code):
    media_kit = get_object_or_404(MediaKit, code=code)
    return render(request, 'vendroid/CRM/mediaKitTemplateV2.html', {
        'media_kit':media_kit,
    })

@login_required(login_url="/login/")
@staff_member_required
def event_invoice_bulk(request):
    user = request.user
    invoices = BulkInvoices.objects.all()
    print 'bulk invoices:   ',invoices
    return render(request, 'vendroid/CRM/bulk_invoices.html', {
        'invoices':invoices,
    })
from dateutil import parser
from datetime import timedelta
@login_required(login_url="/crm/login/")
@staff_member_required
@csrf_exempt
def event_invoice_bulk_create(request):
    form = InvoiceCreationBulkForm()
    invoices_exist = Invoice_Event.objects.filter(is_sent=False).count()
    successMessage = None
    amount = 0
    dateform = DateForm()
    errorMessage = None
    email = None
    ids = None
    invoices = None
    invoices_sent = None
    invoices_generate = None
    agreement_sent = None
    success_message_card = None
    searchForm = SearchForm()
    invoices_sent = None  # EventInvoiceRequest.objects.select_related('event_invoice','event_invoice__register_event').all().order_by('-created_at')[:20]
    if "events_scope" in request.POST:
        events_scope = request.POST.get('events_scope')
        if events_scope == "today":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').filter(
                event_invoice__transaction_id_deposit_date__startswith=datetime.now().date()).order_by('-created_at')
        elif events_scope == "thismonth":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').filter(
                event_invoice__transaction_id_deposit_date__month=datetime.now().date().month).order_by('-created_at')
        elif events_scope == "all":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').all().order_by(
                '-created_at')
        elif events_scope == "pending":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').filter(
                status=EventInvoiceRequest.PENDING).order_by(
                '-created_at')
        elif events_scope == "viewed":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').filter(
                status=EventInvoiceRequest.VIEWED).order_by(
                '-created_at')
        elif events_scope == "paid":
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                       'event_invoice__register_event').filter(
                status=EventInvoiceRequest.PAID).order_by(
                '-created_at')
    else:
        invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice',
                                                                   'event_invoice__register_event').all().order_by(
            '-created_at')[:20]
    if "email" in request.GET:
        if 'card_success_remove' in request.GET:
            success_message_card = 'Card is successfully removed.'
        elif 'card_success_add' in request.GET:
            success_message_card = 'New card is added successfully.'
        email = request.GET['email']
        try:
            email = email.split(' ')[0]
        except:
            return HttpResponseRedirect('/crm/invoices/bulk/create/')
        invoices = InvoiceRegisterVendor.objects.select_related('register','register__event').filter(register__email__iexact=email)
        invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice','event_invoice__register_event').filter(event_invoice__email__iexact=email).order_by('created_at')
        searchForm = SearchForm(initial={
            'email':email,
        })
        agreement_sent = Register_Event_Aggrement.objects.filter(email__iexact=email).order_by('-created_at')
    if request.is_ajax and "make_agreement" in request.POST:
        values_agreement = request.POST.getlist('agreements[]')
        email = request.POST.get('email')
        try:
            email = email.split(' ')[0]
        except:
            return HttpResponseRedirect('/crm/invoices/bulk/create/')
        if values_agreement:
            reg_agg = Register_Event_Aggrement.objects.create(
                                                    email=email.strip(),
                                                    user=request.user,
                                                    code=id_generator(size=20))
            for o in values_agreement:
                reg_eve_add = InvoiceRegisterVendor.objects.get(id=o)
                reg_agg.invoices.add(reg_eve_add)
            context = {
                'message':"Click on the following link to view the agrement <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/crm/view/complete/agreement/%s' target='_blank' class='btn'>Open Agreement</a><br /><br /><b>This agreement will expire in 3 days from the time you view it.</b>"%(reg_agg.code),
                'title':"Bay Area Wedding Fairs Agreement",
                }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement", text_content, 'info@bayareaweddingfairs.com', [reg_agg.email,'wasim@yapjoy.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            return HttpResponse('Select Invoices to generate agreement.')
        return HttpResponse('Done')
    if request.is_ajax and "request_new_card" in request.POST:
        request_new_card = request.POST.get('request_new_card')
        try:
            card_change = CardChange.objects.get(email__iexact=request_new_card)
            if card_change.is_expired:
                card_change.is_expired = False
                card_change.save()
        except:
            card_change = CardChange.objects.create(email=request_new_card)
        context = {
            'message': "Request for card change has been sent to the vandor: %s" % (
            card_change.email),
            'title': "Bay Area Wedding Fairs Card Change Request",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Card Change Request", text_content, 'info@bayareaweddingfairs.com',
                                     ['adeel@yapjoy.com', 'wasim@yapjoy.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        context = {
            'message': "Click on the following link to change your card <br /><br /><a href='https://www.yapjoy.com/invoices/card/change/%s' target='_blank' class='btn'>Change Card</a><br /><br />For more queries please contact info@bayareaweddingfairs.com.</b>" % (
            card_change.code),
            'title': "Bay Area Wedding Fairs Card Change Request",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Card Change Request", text_content, 'info@bayareaweddingfairs.com',
                                     [card_change.email, 'wasim@yapjoy.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse('Done')
    if request.method == "POST":
        if "search_email" in request.POST:
            searchForm = SearchForm(request.POST)
            if searchForm.is_valid():
                data = searchForm.cleaned_data
                email = data['email']
                try:
                    email = email.split(' ')[0]
                except:
                    return HttpResponseRedirect('/crm/invoices/bulk/create/')
                # try:
                invoices = InvoiceRegisterVendor.objects.select_related('register','register__event').filter(register__email__iexact=email)
                invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice','event_invoice__register_event').filter(event_invoice__email__iexact=email).order_by('created_at')
                agreement_sent = Register_Event_Aggrement.objects.filter(email__iexact=email).order_by('-created_at')
        elif "create_bulk_signal" in request.POST:
            email = request.POST.get('email_search')
            try:
                email = email.split(' ')[0]
            except:
                return HttpResponseRedirect('/crm/invoices/bulk/create/')
            ids = request.POST.getlist('bulk_check')
            invoices = InvoiceRegisterVendor.objects.select_related('register','register__event').filter(register__email__iexact=email)
            invoices_sent = EventInvoiceRequest.objects.select_related('event_invoice','event_invoice__register_event').filter(event_invoice__email__iexact=email).order_by('created_at')
            invoices_generate = InvoiceRegisterVendor.objects.filter(id__in=ids).order_by('register__event__date')
            searchForm = SearchForm(initial={
                'email':email,
            })
        elif "no_of_ids" in request.POST:
            no_of_ids = request.POST.get('no_of_ids')
            email = request.POST.get('email_search')
            try:
                email = email.split(' ')[0]
            except:
                return HttpResponseRedirect('/crm/invoices/bulk/create/')
            invoices = InvoiceRegisterVendor.objects.select_related('register','register__event').filter(register__email__iexact=email, is_complete=False)
            total_ids = [str(x) for x in no_of_ids.split(',')]
            list_ids = []
            for o in total_ids:
                if bool(o.strip()):
                    list_ids.append(o.strip())
            invoices_generate = InvoiceRegisterVendor.objects.filter(id__in=list_ids)
            searchForm = SearchForm(initial={
                'email':email,
            })
            is_manual = False
            is_manual_signal = request.POST.get('is_manual', None)
            if is_manual_signal:
                is_manual = True
            ei = EventInvoice.objects.create(email=email,
                                             is_manual=is_manual
                                             )

            deposit_date = request.POST.get('date_deposit')
            balance1_date = request.POST.get('date_balance1')
            balance2_date = request.POST.get('date_balance2')
            balance3_date = request.POST.get('date_balance3')
            if deposit_date:
                ei.deposit_date = (deposit_date)
            if balance1_date:
                ei.balance1_date = (balance1_date)
            if balance2_date:
                ei.balance2_date = (balance2_date)
            if balance3_date:
                ei.balance3_date = (balance3_date)
            ei.code = id_generator(size=50)
            ei.save()
            for o in total_ids:
                if bool(o.strip()):
                    o = o.strip()
                    deposit_str = 'deposit_%s'%(o)
                    balance1_str = 'balance1_%s'%(o)
                    balance2_str = 'balance2_%s'%(o)
                    balance3_str = 'balance3_%s'%(o)
                    deposit_amount = request.POST.get(deposit_str)
                    balance1_amount = request.POST.get(balance1_str)
                    balance2_amount = request.POST.get(balance2_str)
                    balance3_amount = request.POST.get(balance3_str)
                    eid = EventInvoiceDetail.objects.create(event_invoice=ei,
                                                            vendor_register_id=o,
                                                            deposit=(deposit_amount),
                                                            balance1=(balance1_amount),
                                                            balance2=(balance2_amount),
                                                            balance3=(balance3_amount)
                                                            )
                    ei.invoices.add(eid)
                    ei.register_event = eid.vendor_register.register
                    ei.save()
                    iev = InvoiceRegisterVendor.objects.get(id=o)
                    iev.is_complete = True
                    iev.save()
            check_for_invoices(self=None)
            return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s'%(email))
        elif "invoice_recharge_id" in request.POST:
            invoice_recharge_id = request.POST.get('invoice_recharge_id')
            eir = None
            total_amount = 0
            try:
                eir = EventInvoiceRequest.objects.get(id=invoice_recharge_id)
            except Exception as err:
                print err
            e = eir.event_invoice
            invoices_all_pay = e.invoices.all()
            for o in invoices_all_pay:
                if eir.type == EventInvoiceRequest.DEPOSIT:
                    total_amount += o.deposit
                if eir.type == EventInvoiceRequest.BALANCE1:
                    total_amount += o.balance1
                if eir.type == EventInvoiceRequest.BALANCE2:
                    total_amount += o.balance2
                if eir.type == EventInvoiceRequest.BALANCE3:
                    total_amount += o.balance3
            user_ch = User.objects.get(username__iexact=e.email)
            profile_ch = user_ch.userprofile
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                response = stripe.Charge.create(
                    amount=int(100) * (total_amount),  # Convert dollars into cents
                    currency="usd",
                    customer=profile_ch.stripe_id_bawf,
                    description=user_ch.email,
                )
                eir.transaction_id = response.stripe_id
                eir.status = EventInvoiceRequest.PAID
                eir.save()
                if eir.type == EventInvoiceRequest.BALANCE1:
                    e.transaction_id_balance1 = response.stripe_id
                if eir.type == EventInvoiceRequest.BALANCE2:
                    e.transaction_id_balance2 = response.stripe_id
                if eir.type == EventInvoiceRequest.BALANCE3:
                    e.transaction_id_balance3 = response.stripe_id
                e.save()
                context = {
                    'message': "%s (%s)<br /><br />You have been charged successfully with %s pending invoice for event (%s) of $%s.<br /><br />Thank you for working with us.<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (
                    eir.event_invoice.register_event.name, eir.event_invoice.register_event.business_name, eir.type,
                    e.register_event.event.name, str(total_amount)),
                    'title': "Bay Area Wedding Fairs Invoice Charged Successfully",
                }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charged Successfully", text_content,
                                             'info@bayareaweddingfairs.com',
                                             ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as exc:
                print exc
                eir.status = EventInvoiceRequest.FAILED
                eir.save()
                context = {
                    'message': "Dear %s (%s)<br /><br />Your card is failed for auto charge at BayAreaWeddingFairs of %s for the invoice of event (%s) of $%s<br /><br />Failure reason: %s<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (
                    eir.event_invoice.register_event.name, eir.event_invoice.register_event.business_name, eir.type,
                    e.register_event.event.name, str(total_amount), exc),
                    'title': "Bay Area Wedding Fairs Invoice Charge Failed",
                }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charge Failed", text_content,
                                             'info@bayareaweddingfairs.com',
                                             ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s' % (e.email))
        elif "resendAgreement" in request.POST:
            resendAgreement = request.POST.get('resendAgreement')
            email = request.POST.get('email_search')
            try:
                email = email.split(' ')[0]
            except:
                return HttpResponseRedirect('/crm/invoices/bulk/create/')
            agg_reg_resend = Register_Event_Aggrement.objects.get(id=resendAgreement)
            context = {
                'message':"Click on the following link to view the agrement <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/crm/view/complete/agreement/%s' target='_blank' class='btn'>Open Agreement</a><br /><br /><b>This agreement will expire in 3 days from the time you view it.</b>"%(agg_reg_resend.code),
                'title':"Bay Area Wedding Fairs Agreement",
                }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement", text_content, 'info@bayareaweddingfairs.com', [agg_reg_resend.email,'wasim@yapjoy.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s'%(email))
    invoices_id_list = None
    if invoices_generate:
        invoices_id_list = invoices_generate.values_list('id', flat=True)
    register_event = Register_Event.objects.filter(user__email=email)
    event_invoices = EventInvoice.objects.filter(email__iexact=email)
    paid_amount_requested_invoices = 0
    if invoices:
        for inv in invoices:
            amount += inv.get_total()
            if inv.check_invoice_status_paid_amount() == "Paid":
                paid_amount_requested_invoices += inv.get_total()
    customer_failed = None
    is_customer = None
    card_errors = None
    profile = None
    if email:
        try:
            user = User.objects.get(email__iexact=email)
            profile = user.userprofile
            if profile.stripe_id_bawf:
                stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                is_customer_data = stripe.Customer.retrieve(
                    profile.stripe_id_bawf)  # .cards.all(limit=1)['data'][0]['last4']
                is_customer = is_customer_data.sources['data'][0]['last4']
        except Exception as e:
            print 'inside customer exception: ',e
            customer_failed = True
    if 'removeCard' in request.POST:
        email = request.POST.get('search_email')
        try:
            email = email.split(' ')[0]
        except:
            return HttpResponseRedirect('/crm/invoices/bulk/create/')
        user = User.objects.get(email__iexact=email)
        profile = user.userprofile
        profile.stripe_id_bawf = ''
        profile.save()
        success_message_card = "Card is successfully removed."
        return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s&card_success_remove=True' % (email))
    cc_form = CreditCardCreationForm()
    if 'stripe_token' in request.POST:
        email = request.POST.get('search_email')
        try:
            email = email.split(' ')[0]
        except:
            return HttpResponseRedirect('/crm/invoices/bulk/create/')
        user = User.objects.get(username__iexact=email)
        profile = user.userprofile
        stripe_token = request.POST.get('stripe_token')
        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
        try:
            stripe_customer = stripe.Customer.create(
                email=user.email,
                card=request.POST.get("stripe_token")
            )
            if stripe_customer:
                profile.stripe_id_bawf = stripe_customer.id
                profile.save()
            return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s&card_success_add=True' % (email))
        except Exception as e:
            print e
            card_errors = str(e)
    public_key = settings.STRIPE_PUBLISHABLE_KEY_BAWF
    pending_invoices = EventInvoiceDetail.objects.select_related('event_invoice','event_invoice__register_event__event','event_invoice__register_event').filter(event_invoice__email__iexact=email)
    if 'edit_pending_invoice' in request.POST:
        edit_pending_invoice = request.POST.get('edit_pending_invoice')
        edit_pending_invoice_type = request.POST.get('edit_pending_invoice_type')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        eid_edit = EventInvoiceDetail.objects.get(id=edit_pending_invoice)
        amount = int(str(amount))
        if edit_pending_invoice_type == "deposit":
            eid_ei_main = eid_edit.vendor_register
            if amount > eid_edit.deposit:
                eid_ei_main.offered_price += (amount-eid_edit.deposit)
            else:
                eid_ei_main.offered_price -= abs(amount - eid_edit.deposit)
            eid_edit.deposit = amount
            eid_ei = eid_edit.event_invoice
            eid_ei.deposit_date = date
            eid_ei_main.save()
            eid_ei.save()
            eid_edit.save()
        if edit_pending_invoice_type == "balance1":
            eid_ei_main = eid_edit.vendor_register
            if amount > eid_edit.balance1:
                eid_ei_main.offered_price += (amount - eid_edit.balance1)
            else:
                eid_ei_main.offered_price -= abs(amount - eid_edit.balance1)
            eid_edit.balance1 = amount
            eid_ei = eid_edit.event_invoice
            eid_ei.balance1_date = date
            eid_ei_main.save()
            eid_ei.save()
            eid_edit.save()
        if edit_pending_invoice_type == "balance2":
            eid_ei_main = eid_edit.vendor_register
            if amount > eid_edit.balance2:
                eid_ei_main.offered_price += (amount - eid_edit.balance2)
            else:
                eid_ei_main.offered_price -= abs(amount - eid_edit.balance2)
            eid_edit.balance2 = amount
            eid_ei = eid_edit.event_invoice
            eid_ei.balance2_date = date
            eid_ei_main.save()
            eid_ei.save()
            eid_edit.save()
        if edit_pending_invoice_type == "balance3":
            eid_ei_main = eid_edit.vendor_register
            if amount > eid_edit.balance3:
                eid_ei_main.offered_price += (amount - eid_edit.balance3)
            else:
                eid_ei_main.offered_price -= abs(amount - eid_edit.balance3)
            eid_edit.balance3 = amount
            eid_ei = eid_edit.event_invoice
            eid_ei.balance3_date = date
            eid_ei_main.save()
            eid_ei.save()
            eid_edit.save()
        check_for_invoices(None)
        return HttpResponseRedirect('/crm/invoices/bulk/create/?email=%s&card_success_add=True' % (email))
    if 'resendoldagreement' in request.POST:
        invoice_resend_id = request.POST.get('invoice_resend_id')
        invoice_req = EventInvoiceRequest.objects.get(id=invoice_resend_id)
        agree_req = Register_Event_Aggrement.objects.get(id=invoice_req.agreement_code)
        context = {
            'message': "%s (%s)<br /><br />Click on the following link to view the agreement. <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/invoices/deposit/pay/%s/%s' target='_blank' class='btn'>Open Agreement</a>"%(invoice_req.event_invoice.register_event.name,invoice_req.event_invoice.register_event.business_name,invoice_req.code,agree_req.code),
            'title': "Bay Area Wedding Fairs Agreement",
        }
        html_content = render_to_string('email/bawf_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement", text_content, 'info@bayareaweddingfairs.com',
                                     ['info@bayareaweddingfairs.com', agree_req.email], bcc=['adeel@yapjoy.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        agree_req.status = Register_Event_Aggrement.PENDING
        agree_req.save()
        successMessage = "(Deposit Invoice / Agreement) has been resent to %s"%(agree_req.email)
    if "invoice_remove_id" in request.POST:
        invoice_remove_id = request.POST.get('invoice_remove_id')
        eir_remove = EventInvoiceRequest.objects.get(id=invoice_remove_id)
        email = eir_remove.event_invoice.email
        remove_invoices = eir_remove.event_invoice.invoices.all()
        for remove_invoice in remove_invoices:
            reg_ven = remove_invoice.vendor_register
            eve_inv = reg_ven.register
            eve_inv.have_invoices -= 1
            eve_inv.save()
            reg_ven.delete()
            ri_vr = eir_remove.event_invoice.register_event
            ri_vr.amount_due = ri_vr.get_amount_due()
            ri_vr.total_amount = ri_vr.get_amount_total()
            ri_vr.save()
        eir_remove.event_invoice.invoices.all().delete()
        try:
            Register_Event_Aggrement.objects.get(id=eir_remove.agreement_code).delete()
        except Exception as e:
            print "Exception inside deleting the agreement: ",e
        er_ei = eir_remove.event_invoice
        er_ei.delete()
        eir_remove.delete()
        return HttpResponseRedirect('?email=%s'%(email))
    elif "invoice_cancel_id" in request.POST:
        invoice_cancel_id = request.POST.get('invoice_cancel_id')
        inv_req = EventInvoiceRequest.objects.get(id=invoice_cancel_id)
        inv_req.status = EventInvoiceRequest.CANCEL
        inv_req.cancel_date = datetime.now()
        inv_req.cancelled_by_id = request.user.id
        inv_req.save()
    elif "invoice_uncancel_id" in request.POST:
        invoice_cancel_id = request.POST.get('invoice_uncancel_id')
        inv_req = EventInvoiceRequest.objects.get(id=invoice_cancel_id)
        inv_req.status = EventInvoiceRequest.PENDING
        inv_req.save()
    return render(request, 'vendroid/CRM/bulk_invoices_create.html', {
        'card_errors':card_errors,
        'public_key':public_key,
        'is_customer':is_customer,
        'cc_form':cc_form,
        'customer_failed':customer_failed,
        'profile':profile,
        'success_message_card':success_message_card,
        'form':form,
        'successMessage':successMessage,
        'invoices_exist':invoices_exist,
        'searchForm':searchForm,
        'errorMessage':errorMessage,
        'invoices':invoices,
        'total':amount,
        'paid_amount_requested_invoices':paid_amount_requested_invoices,
        'email':email,
        'invoices_generate_ids':invoices_id_list,
        'invoices_generate':invoices_generate,
        'event_invoices':event_invoices,
        'dateform':dateform,
        'invoices_sent':invoices_sent,
        'agreement_sent':agreement_sent,
        'pending_invoices':pending_invoices,
    })


def check_for_invoices_automatic(self):
    yesterday = datetime.today() - timedelta(2)
    invoices_to_run__objects = EventInvoice.objects.filter(is_manual=False, deposit_date__icontains=yesterday.date())
    if invoices_to_run__objects:
        for e in invoices_to_run__objects:
            # print e.deposit_date, e.id
            text_to_append = ""
            try:
                event_obj = e.register_event
                if event_obj:
                    if event_obj.is_partner_vendor:
                        text_to_append = "<br /><br />You have been offered Partner Vendor status. One of the benefits of being a partner vendor is that your business is listed on BayAreaWeddingFairs.com website<br />Please send us following so we can list you on our website.<br /><br /><li>A 400x400 pixel picture with your business logo</li><li>Your business website link (URL)</li><li>Contact Information</li><li>A 60 word description of your business.</li><br /><br />Please send this information to Steve@BayAreaWeddingFairs.com<br /><br />Thank you"
            except Exception as e:
                print "partner vendor failed: ", e
            try:
                eir = None
                print '-----------------------------------------------------'
                print e.id
                print e.deposit_date, datetime.today().date()
                req_inv = EventInvoiceRequest.objects.filter(event_invoice=e)
                deposit_req_inv = req_inv.filter(type=EventInvoiceRequest.DEPOSIT)
                print deposit_req_inv
                if e.deposit_date == yesterday.date() and deposit_req_inv:
                    print 'works'
                    invoice = deposit_req_inv[0]#EventInvoiceRequest.objects.get(event_invoice=e)
                    if not e.transaction_id_deposit:
                        charge = None
                        print 'inside deposit trans'
                        total_amount = 0
                        # try:
                        # print code
                        # invoice = req_inv
                        if not invoice.status == EventInvoiceRequest.CANCEL:
                            user = None
                            profile = None
                            # try:
                            print 'getting user'
                            user = User.objects.get(email__iexact=invoice.event_invoice.email,
                                                    username__iexact=invoice.event_invoice.email)
                            # except:
                            #     user = User.objects.create(email__iexact=invoice.event_invoice.email,
                            #                                username__iexact=invoice.event_invoice.email)
                            #     user.first_name = invoice.event_invoice.register_event.name
                            #     user.save()
                            profile = user.userprofile
                            # user.backend = 'django.contrib.auth.backends.ModelBackend'
                            # auth_login(request, user)
                            # print invoice.status
                            # if invoice.status == EventInvoiceRequest.PENDING:
                            #     invoice.status = EventInvoiceRequest.VIEWED
                            #     invoice.save()

                            type = invoice.type
                            print type
                            invoices = invoice.event_invoice.invoices.all()
                            for o in invoices:
                                if type == EventInvoiceRequest.DEPOSIT:
                                    total_amount += o.deposit
                                if type == EventInvoiceRequest.BALANCE1:
                                    total_amount += o.balance1
                                if type == EventInvoiceRequest.BALANCE2:
                                    total_amount += o.balance2
                                if type == EventInvoiceRequest.BALANCE3:
                                    total_amount += o.balance3
                                    # if o.vendor_register.email_list:
                                    #     is_list = True
                                    # invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, registered_event__email=user.email)
                                    # event = invoice.registered_event.event
                                    # if not invoice.is_signed:
                                    #     return HttpResponseRedirect('/invoices/')
                        # except Exception as e:
                        #     print e
                        #     raise Http404
                        #     try:
                            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                            charge = stripe.Charge.create(
                                amount=(total_amount * 100),  # in cents
                                currency="usd",
                                customer=profile.stripe_id_bawf)
                #             except Exception as e:
                #                 charge = None
                #                 error_message = e
                #             if charge:
                            # invoice.payment_date = datetime.now().date()
                            invoice.transaction_id = charge.stripe_id
                            invoice.status = EventInvoiceRequest.PAID
                            invoice.save()
                            e_invoice = invoice.event_invoice
                            e_invoice.transaction_id_deposit = charge.stripe_id
                            e_invoice.save()
                            e_invoice.transaction_id_deposit_date = datetime.now()
                            e_invoice.save()
                            reg_event = e_invoice.register_event
                            # reg_event.record_amount_due()
                            # Register_Event_Aggrement.objects.get()
                            # agreement.status = Register_Event_Aggrement.ACCEPTED
                            # agreement.save()

                            context = {
                                'message': "%s (%s) with email %s, invoice with id: %s is paid through the system successfully." % (
                                invoice.event_invoice.register_event.name,
                                invoice.event_invoice.register_event.business_name, user.email, e.id),
                                'title': "System charge successful: Bay Area Wedding Fairs Agreement",
                            }
                            html_content = render_to_string('email/bawf_native_email.html', context=context)
                            text_content = strip_tags(html_content)
                            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                                         'info@bayareaweddingfairs.com',
                                                         ['info@bayareaweddingfairs.com', 'adeel@yapjoy.com'])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            context = {
                                'message': "Thank you for accepting the agreement for following show(s) %s. This email confirms your deposit (payment) of $%s. We look forward to working with you. If you have any questions or concerns, please contact your salesperson or email us at info@BayAreaWeddingFairs.com %s" % (e.get_shows(),
                                    total_amount, text_to_append),
                                'title': "Accepted Bay Area Wedding Fairs Agreement",
                            }
                            html_content = render_to_string('email/bawf_native_email.html', context=context)
                            text_content = strip_tags(html_content)
                            msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted",
                                                         body=text_content,
                                                         from_email='info@bayareaweddingfairs.com',
                                                         to=[user.email],
                                                         cc=['info@bayareaweddingfairs.com'])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            print 'e_invoice.transaction_id_deposit: ', e_invoice.transaction_id_deposit
                            print '------------------- amount due 1: ', reg_event.amount_due
                            print '------------------- amount due 1 func: ', reg_event.get_amount_due()
                            print '------------------- total amount 1: ', reg_event.total_amount
                            print '------------------- total amount 1 func: ', reg_event.get_amount_total()
                            print 'e_invoice.transaction_id_deposit: ', e_invoice.transaction_id_deposit
                            reg_event.amount_due = reg_event.get_amount_due()
                            reg_event.total_amount = reg_event.get_amount_total()
                            reg_event.save()
                            print '------------------- amount due 2: ', reg_event.amount_due
                            print '------------------- total amount 2: ', reg_event.total_amount
                            # else:

            except Exception as ExcFin:
                print "Exception: ",ExcFin
                context = {
                    'message': "Email: %s<br /><br />%s"%(e.email, ExcFin),
                    'title': "System charge failed",
                }
                html_content = render_to_string('email/bawf_native_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("System charge failed", text_content,
                                             'info@bayareaweddingfairs.com',
                                             ['info@bayareaweddingfairs.com', 'adeel@yapjoy.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

    # eir = EventInvoiceRequest.objects.create(code=id_generator(size=50), event_invoice=ei)
    # context = {
    #     'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(eir.code),
    #     'title':"Bay Area Wedding Fairs Invoice",
    #     }
    # html_content = render_to_string('email/bawf_email.html', context=context)
    # text_content = strip_tags(html_content)
    # msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',ei.email])
    # msg.attach_alternative(html_content, "text/html")
    # msg.send()
    # print no_of_ids


def check_for_invoices(self):
    event_invoices_objects = EventInvoice.objects.all().exclude(is_cancelled=True)
    for e in event_invoices_objects:
        try:
            eir = None
            print '-----------------------------------------------------'
            print e.id
            print e.deposit_date, datetime.today().date()
            print e.balance1_date, datetime.today().date()
            print e.balance2_date, datetime.today().date()
            print e.balance3_date, datetime.today().date()
            req_inv = EventInvoiceRequest.objects.filter(event_invoice=e)
            deposit_req_inv = req_inv.filter(type=EventInvoiceRequest.DEPOSIT)
            balance1_req_inv = req_inv.filter(type=EventInvoiceRequest.BALANCE1)
            balance2_req_inv = req_inv.filter(type=EventInvoiceRequest.BALANCE2)
            balance3_req_inv = req_inv.filter(type=EventInvoiceRequest.BALANCE3)
            if e.deposit_date == datetime.today().date():
                if not e.transaction_id_deposit and not deposit_req_inv:
                    eir = None
                    us_reg = None
                    reg_agg = None
                    print 'inside deposit date'
                    try:
                        print "Working here"
                        eir = EventInvoiceRequest.objects.get(event_invoice=e,
                                                              type=EventInvoiceRequest.DEPOSIT)

                    except Exception as err:
                        print err
                        eir = EventInvoiceRequest.objects.create(code=id_generator(size=50),
                                                                 event_invoice=e,
                                                                 type=EventInvoiceRequest.DEPOSIT)
                    print e.email
                    us_reg = User.objects.get(username__iexact=e.email)
                    reg_agg = Register_Event_Aggrement.objects.create(
                        email=e.email,
                        user=us_reg,
                        code=id_generator(size=20))
                    eir.agreement_code = reg_agg.id
                    eir.save()

                    # reg_eve_add = InvoiceRegisterVendor.objects.filter(register=e.register_event)
                    # for obj_rea in reg_eve_add:
                    for obj_rea in e.invoices.all():
                        reg_agg.invoices.add(obj_rea.vendor_register)
                        reg_agg.save()
                    if eir:
                        context = {}
                        if e.is_manual:
                            context = {
                                    'message':"%s (%s)<br /><br />Click on the following link to view the agreement. <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/invoices/deposit/pay/%s/%s' target='_blank' class='btn'>Open Agreement</a><br /><br /><b>This agreement will expire in 3 days from the time you view it.</b>"%(eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name,eir.code,reg_agg.code),
                                    'title':"Bay Area Wedding Fairs Agreement",
                                    }
                        else:
                            context = {
                                    'message':"%s (%s)<br /><br />The agreement will automatically go into full effect within 24 hours of the send time posted on this email. Please make sure you review this agreement immediately and contact your representative if something has been omitted or is incorrectly stated. Once the 24 hour review period has passed and no concerns have been brought to our attention, all intents and concerns stated within this agreement will become fully bound. If you have posted immediate payment it also will complete within 24 hours of the posted email time. Therefore it is paramount that you review and accept this agreement within the specified time.<br /><br />Please click on the link below to review your full agreement. We look forward to working with you. Please reach out to your representative immediately if anything is confusing or incorrect within the agreement so it can be adjusted prior to the specified 24 hour binding period. <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/invoices/deposit/pay/%s/%s' target='_blank' class='btn'>Open Agreement</a><br /><br /><b>This agreement will expire in 3 days from the time you view it.</b>"%( eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name,eir.code,reg_agg.code),
                                    'title':"Bay Area Wedding Fairs Agreement",
                                    }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',e.email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        e_r_e = e.register_event
                        # e_r_e.record_amount_due()
                        e_r_e.amount_due = e_r_e.get_amount_due()
                        e_r_e.total_amount = e_r_e.get_amount_total()
                        e_r_e.save()
                        print 'email sent to : ',e.email
            if e.balance1_date == datetime.today().date() and not balance1_req_inv and e.transaction_id_deposit:
                if not e.transaction_id_balance1:
                    eir = None
                    total_amount = 0
                    print "send balance 1"

                    try:
                        eir = EventInvoiceRequest.objects.get(event_invoice=e,
                                                              type=EventInvoiceRequest.BALANCE1)
                    except Exception as err:
                        print err
                        eir = EventInvoiceRequest.objects.create(code=id_generator(size=50),
                                                                 event_invoice=e,
                                                                 type=EventInvoiceRequest.BALANCE1)
                    invoices_all_pay = e.invoices.all()
                    for o in invoices_all_pay:
                        if eir.type == EventInvoiceRequest.DEPOSIT:
                            total_amount += o.deposit
                        if eir.type == EventInvoiceRequest.BALANCE1:
                            total_amount += o.balance1
                        if eir.type == EventInvoiceRequest.BALANCE2:
                            total_amount += o.balance2
                        if eir.type == EventInvoiceRequest.BALANCE3:
                            total_amount += o.balance3
                    # email = e.email
                    print total_amount
                    user = User.objects.get(username__iexact=e.email)
                    profile = user.userprofile
                    try:
                        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                        response = stripe.Charge.create(
                            amount=int(100) * (total_amount),  # Convert dollars into cents
                            currency="usd",
                            customer=profile.stripe_id_bawf,
                            description=user.email,
                        )
                        eir.transaction_id = response.stripe_id
                        eir.status = EventInvoiceRequest.PAID
                        eir.save()
                        e.transaction_id_balance1 = response.stripe_id
                        e.save()
                        e.transaction_id_balance1_date = e.get_transaction_id_balance1_date()
                        e.save()
                        context = {
                                    'message':"Dear %s (%s)<br /><br />You have been charged successfully with balance 1 ($%s) pending invoice for event (%s).<br /><br />Thank you for working with us.<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://bayareaweddingfairs.herokuapp.com/feedback/'> Support Feedback</a> form."%(eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount),eir.get_event_b1()),
                                    'title':"Bay Area Wedding Fairs Invoice Charged Successfully",
                                }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charged Successfully", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',e.email], bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        e_r_e = e.register_event
                        # e_r_e.record_amount_due()
                        e_r_e.amount_due = e_r_e.get_amount_due()
                        e_r_e.total_amount = e_r_e.get_amount_total()
                        e_r_e.save()
                    except Exception as exc:
                        print exc
                        eir.status = EventInvoiceRequest.FAILED
                        eir.save()
                        context = {
                            'message': "Dear %s (%s)<br /><br />Your card is failed for auto charge at BayAreaWeddingFairs of Balance 1 ($%s) for the invoice of event (%s).<br /><br />Failure reason: %s<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount),eir.get_event_b1(), exc),
                            'title': "Bay Area Wedding Fairs Invoice Charge Failed",
                        }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charge Failed", text_content,
                                                     'info@bayareaweddingfairs.com',
                                                     ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    # if eir:
                    #     context = {
                    #             'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/invoices/pay/%s' target='_blank' class='btn'>Open Invoice</a>"%(eir.code),
                    #             'title':"Bay Area Wedding Fairs Invoice",
                    #             }
                    #     html_content = render_to_string('email/bawf_email.html', context=context)
                    #     text_content = strip_tags(html_content)
                    #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',e.email])
                    #     msg.attach_alternative(html_content, "text/html")
                    #     msg.send()
                    #     print 'email sent to : ',e.email
            if e.balance2_date == datetime.today().date() and not balance2_req_inv and e.transaction_id_deposit:
                if not e.transaction_id_balance2:
                    eir = None
                    total_amount = 0

                    print "send balance 2"
                    try:
                        eir = EventInvoiceRequest.objects.get(event_invoice=e,
                                                              type=EventInvoiceRequest.BALANCE2)
                    except Exception as err:
                        print err
                        eir = EventInvoiceRequest.objects.create(code=id_generator(size=50),
                                                                 event_invoice=e,
                                                                 type=EventInvoiceRequest.BALANCE2)
                    invoices_all_pay = e.invoices.all()
                    for o in invoices_all_pay:
                        if eir.type == EventInvoiceRequest.DEPOSIT:
                            total_amount += o.deposit
                        if eir.type == EventInvoiceRequest.BALANCE1:
                            total_amount += o.balance1
                        if eir.type == EventInvoiceRequest.BALANCE2:
                            total_amount += o.balance2
                        if eir.type == EventInvoiceRequest.BALANCE3:
                            total_amount += o.balance3
                    # email = e.email
                    print total_amount
                    user = User.objects.get(username__iexact=e.email)
                    profile = user.userprofile
                    try:
                        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                        response = stripe.Charge.create(
                            amount=int(100) * (total_amount),  # Convert dollars into cents
                            currency="usd",
                            customer=profile.stripe_id_bawf,
                            description=user.email,
                        )
                        eir.transaction_id = response.stripe_id
                        eir.status = EventInvoiceRequest.PAID
                        eir.save()
                        e.transaction_id_balance2 = response.stripe_id
                        e.save()
                        e.transaction_id_balance2_date = e.get_transaction_id_balance2_date()
                        e.save()
                        context = {
                            'message': "Dear %s (%s)<br /><br />You have been charged successfully with balance 2 ($%s) pending invoice for event (%s).<br /><br />Thank you for working with us.<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount), eir.get_event_b2()),
                            'title': "Bay Area Wedding Fairs Invoice Charged Successfully",
                        }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charged Successfully",
                                                     text_content, 'info@bayareaweddingfairs.com',
                                                     ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        e_r_e = e.register_event
                        # e_r_e.record_amount_due()
                        e_r_e.amount_due = e_r_e.get_amount_due()
                        e_r_e.total_amount = e_r_e.get_amount_total()
                        e_r_e.save()
                    except Exception as exc:
                        print exc
                        eir.status = EventInvoiceRequest.FAILED
                        eir.save()
                        context = {
                            'message': "Dear %s (%s)<br /><br />Your card is failed for auto charge at BayAreaWeddingFairs of Balance 2 ($%s) for the invoice of event (%s).<br /><br />Failure reason: %s<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount), eir.get_event_b2(), exc),
                            'title': "Bay Area Wedding Fairs Invoice Charge Failed",
                        }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charge Failed", text_content,
                                                     'info@bayareaweddingfairs.com',
                                                     ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    # if eir:
                    #     context = {
                    #             'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/invoices/pay/%s' target='_blank' class='btn'>Open Invoice</a>"%(eir.code),
                    #             'title':"Bay Area Wedding Fairs Invoice",
                    #             }
                    #     html_content = render_to_string('email/bawf_email.html', context=context)
                    #     text_content = strip_tags(html_content)
                    #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',e.email])
                    #     msg.attach_alternative(html_content, "text/html")
                    #     msg.send()
                    #     print 'email sent to : ',e.email
            if e.balance3_date == datetime.today().date() and not balance3_req_inv and e.transaction_id_deposit:
                if not e.transaction_id_balance3:
                    eir = None
                    total_amount = 0
                    print "send balance 3"
                    try:
                        eir = EventInvoiceRequest.objects.get(event_invoice=e,
                                                              type=EventInvoiceRequest.BALANCE3)
                    except Exception as err:
                        print err
                        eir = EventInvoiceRequest.objects.create(code=id_generator(size=50),
                                                                 event_invoice=e,
                                                                 type=EventInvoiceRequest.BALANCE3)
                    invoices_all_pay = e.invoices.all()
                    for o in invoices_all_pay:
                        if eir.type == EventInvoiceRequest.DEPOSIT:
                            total_amount += o.deposit
                        if eir.type == EventInvoiceRequest.BALANCE1:
                            total_amount += o.balance1
                        if eir.type == EventInvoiceRequest.BALANCE2:
                            total_amount += o.balance2
                        if eir.type == EventInvoiceRequest.BALANCE3:
                            total_amount += o.balance3
                    # email = e.email
                    print total_amount
                    user = User.objects.get(username__iexact=e.email)
                    profile = user.userprofile
                    try:
                        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
                        response = stripe.Charge.create(
                            amount=int(100) * (total_amount),  # Convert dollars into cents
                            currency="usd",
                            customer=profile.stripe_id_bawf,
                            description=user.email,
                        )
                        eir.transaction_id = response.stripe_id
                        eir.status = EventInvoiceRequest.PAID
                        eir.save()
                        e.transaction_id_balance3 = response.stripe_id
                        e.save()
                        e.transaction_id_balance3_date = e.get_transaction_id_balance3_date()
                        e.save()
                        context = {
                            'message': "Dear %s (%s)<br /><br />You have been charged successfully with balance 3 ($%s) pending invoice for event (%s).<br /><br />Thank you for working with us.<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount), eir.get_event_b3()),
                            'title': "Bay Area Wedding Fairs Invoice Charged Successfully",
                        }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charged Successfully",
                                                     text_content, 'info@bayareaweddingfairs.com',
                                                     ['info@bayareaweddingfairs.com', e.email], bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        e_r_e = e.register_event
                        # e_r_e.record_amount_due()
                        e_r_e.amount_due = e_r_e.get_amount_due()
                        e_r_e.total_amount = e_r_e.get_amount_total()
                        e_r_e.save()
                    except Exception as exc:
                        print exc
                        eir.status = EventInvoiceRequest.FAILED
                        eir.save()
                        context = {
                            'message': "Dear %s (%s)<br /><br />Your card is failed for auto charge at BayAreaWeddingFairs of Balance 3 ($%s) for the invoice of event (%s).<br /><br />Failure reason: %s<br /><br />For any queries, feel free to contact info@bayareaweddingfairs.com or use our <a href='https://www.yapjoy.com/feedback/'> Support Feedback</a> form." % (eir.event_invoice.register_event.name,eir.event_invoice.register_event.business_name, str(total_amount), eir.get_event_b3(), exc),
                            'title': "Bay Area Wedding Fairs Invoice Charge Failed",
                        }
                        html_content = render_to_string('email/bawf_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("Bay Area Wedding Fairs Invoice Charge Failed", text_content,
                                                     'info@bayareaweddingfairs.com',
                                                     ['info@bayareaweddingfairs.com', e.email],bcc=['adeel@yapjoy.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    # if eir:
                    #     context = {
                    #             'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/invoices/pay/%s' target='_blank' class='btn'>Open Invoice</a>"%(eir.code),
                    #             'title':"Bay Area Wedding Fairs Invoice",
                    #             }
                    #     html_content = render_to_string('email/bawf_email.html', context=context)
                    #     text_content = strip_tags(html_content)
                    #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',e.email])
                    #     msg.attach_alternative(html_content, "text/html")
                    #     msg.send()
                    #     print 'email sent to : ',e.email
        except Exception as ExcFin:
            print ExcFin

    # eir = EventInvoiceRequest.objects.create(code=id_generator(size=50), event_invoice=ei)
    # context = {
    #     'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(eir.code),
    #     'title':"Bay Area Wedding Fairs Invoice",
    #     }
    # html_content = render_to_string('email/bawf_email.html', context=context)
    # text_content = strip_tags(html_content)
    # msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com',ei.email])
    # msg.attach_alternative(html_content, "text/html")
    # msg.send()
    # print no_of_ids

import csv as csv_import
from yapjoy.settings import MEDIA_URL, BASE_DIR
@login_required(login_url='/login/')
@staff_member_required
def invoices_data(request):
    user = request.user
    successMessage = None
    events = csvUpload.objects.all().order_by('-created_at')
    form = csvform()
    message = None
    if request.method == "POST":
        if "delete_id" in request.POST:
            delete_id = request.POST.get('delete_id')
            try:
                csv = csvUpload.objects.get(id=delete_id)
                csv.delete()
                successMessage = "CSV is deleted successfully."
            except:
                raise Http404
        else:
            form = csvform(request.POST, request.FILES)
            if form.is_valid():
                # 'name','csv','is_visible'
                print "form is valid"
                data = form.cleaned_data
                print data
                # form.csv.save()
                # form.save()
                name = request.FILES['csv'].name
                file = request.FILES['csv']
                sub = request.POST['name']
                is_visible = request.POST['is_visible']
                csv_obj = csvUpload.objects.create(name=sub, csv=file, is_visible=is_visible)
                print name
                download_file('%sstatic/%s'%(MEDIA_URL, name))
                save_file(name)
                print 'file is saved'
                print 'opening the file'
                objects = []
                with open(name, 'rU') as f:
                    print "script started"
                    reader = csv_import.reader(f)
                    next(reader, None)
                    mylist = []

                    'starting the row'
                    for row in reader:
                        first_name = row[0]
                        last_name = row[1]
                        email = row[2]
                        phone = row[3]
                        city = row[4]
                        state = row[5]
                        zip = row[6]
                        wedding_date = row[7]
                        print first_name, last_name, email, phone, city, state, zip, wedding_date

                        objects.append(csvData(csv=csv_obj,
                                               first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               phone=phone,
                                               city=city,
                                               state=state,
                                               zip=zip,
                                               wedding_date=wedding_date))
                    csvData.objects.bulk_create(objects)
                    csv_obj.csv.delete()
                    successMessage = "CSV is uploaded successfully."
    print events
    return render(request, 'vendroid/CRM/data_list.html', {
        'events':events,
        'form':form,
        'successMessage':successMessage,
    })
from django.shortcuts import get_object_or_404
@login_required(login_url='/login/')
@staff_member_required
def invoices_data_view(request, id):
    try:
        events = csvUpload.objects.get(id=id)
    except Exception as e:
        raise Http404
    csvdata = csvData.objects.filter(csv=events)
    return render(request, 'vendroid/CRM/data_list_view.html', {
        'events':events,
        'csvdata':csvdata,
    })

@login_required(login_url='/crm/login/')
def invoicesdataview_list(request, id):
    try:
        user = request.user
        uploadedCSV = csvUpload.objects.get(id=id)
        purchase = UserCSV.objects.get(user=user, csv=uploadedCSV)
    except Exception as e:
        raise Http404
    csvdata = csvData.objects.select_related('csv').filter(csv=uploadedCSV)#.values('first_name','last_name','email')
    return render(request, 'vendroid/CRM/data_list_view_user.html', {
        'events':uploadedCSV,
        'csvdata':csvdata,
    })


from billing import CreditCard, get_gateway
import stripe
from yapjoy import settings
from yapjoy_accounts.models import Transaction, TransactionHistory

@login_required(login_url='/login/')
def CSVBuyiFrameCoin(request, id):
    print id
    credit = None
    credits = None
    reload_window = None
    # try:
    #     credit = CreditPackages.objects.get(id=id)
    #     credits = CreditPackages.objects.all().exclude(id=id)
    # except:
    #     raise Http404
    # initial = {}
    customer_failed = False
    is_customer = None
    amount = None
    stripeError = ""
    user = request.user
    userprofile = user.userprofile
    successMessage = None
    event = None
    try:
        event = csvUpload.objects.get(id=id)
    except Exception as e:
        print e
        raise Http404
    initial = {
        # 'name':'A k',
        # 'number':'4242424242424242',
        # 'verification_value':'112',
        # 'month':'01',
        # 'year':'2017',
        # 'amount':'10',
    }
    # try:
    #     if userprofile.stripe_id:
    #         stripe.api_key = settings.STRIPE_SECRET_KEY
    #         is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
    #         print 'is customer: ',is_customer_data.sources['data'][0]['last4']
    #         is_customer = is_customer_data.sources['data'][0]['last4']
    # except:
    #     customer_failed = True
    form = CreditCardDepositConfirmFormCoin()
    if request.method == "POST":
        if "cc_form_submit" in request.POST:
            form = CreditCardDepositConfirmFormCoin(request.POST)
            if form.is_valid():
                try:
                    print 'valid'
                    data = form.cleaned_data
                    amount_coins = 10
                    # name = data['name']
                    number = data['number']
                    month = data['month']
                    year = data['year']
                    # pledge = data['package']
                    # verification_value = data['verification_value']
                    merchant = get_gateway("modified_stripe")
                    stripe_token = request.POST.get("stripe_token")
                    print 'stripe token: ', stripe_token
                    print 'inside CC'
                    # stripe.api_key = settings.STRIPE_SECRET_KEY
                    stripe.api_key = "sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0"
                    stripe_customer = stripe.Customer.create(
                        email=user.email,
                        card=request.POST.get("stripe_token")
                    )
                    print 'customer: ',stripe_customer

                    # if stripe_customer:
                    userprofile.stripe_id = stripe_customer.id
                    userprofile.save()
                    print 'about to response'
                    response = stripe.Charge.create(
                        amount=int(100) * (event.amount),  # Convert dollars into cents
                        currency="usd",
                        customer=userprofile.stripe_id,
                        description=user.email,
                    )

                    # try:
                    #     if userprofile.stripe_id:
                    #         stripe.api_key = settings.STRIPE_SECRET_KEY
                    #         is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
                    #         print 'is customer: ',is_customer_data.sources['data'][0]['last4']
                    #         is_customer = is_customer_data.sources['data'][0]['last4']
                    # except:
                    #     pass
                    print response
                    if response:  # handle invalid response
                        print 'PAYMENT DONE'
                        # userprofile.subscribed=True
                        Transaction.objects.create(user=user, amount =str(event.amount), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                        TransactionHistory.objects.create(user=user, event="Purchased the csv: %s."%(event.name), amount=int(event.amount))
                        # userprofile.amount += pledge.credits
                        # userprofile.save()
                        reload_window = 'Reload'
                        # try:
                        #     from yapjoy_registration.models import SubscribedUsers
                        #     SubscribedUsers.objects.create(user=user, no_of_months=1, amount=10)
                        # except:
                        #     pass
                        UserCSV.objects.create(user=user, csv=event)
                        successMessage = "%s is purchased successfully."%(event.name)
                        # send_donation_email(tplVar, user.email)
                        # return HttpResponseRedirect('/account/')
                except Exception as e:
                    print 'here error:', e
                    stripeError = "Your card was declined."
        elif "cc_form_submit_cus" in request.POST:
            amount = 10
            if not amount == "" or amount == "None":
                try:
                    amountCheck = int(str(10))
                    if amountCheck == None or amountCheck == 0:
                        pass
                    else:
                        # stripe.api_key = settings.STRIPE_SECRET_KEY
                        stripe.api_key = "sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0"
                        response = stripe.Charge.create(
                        amount=int(100) * event.amount,  # Convert dollars into cents
                        currency="usd",
                        customer=userprofile.stripe_id,
                        description=user.email,
                        )
                        print response
                        if response:  # handle invalid response
                            print 'PAYMENT DONE'
                            Transaction.objects.create(user=user, amount =str(event.amount), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                            TransactionHistory.objects.create(user=user, event="Purchased the csv: %s."%(event.name), amount=int(event.amount))

                            # userprofile.subscribed=True
                            # userprofile.amount += 10
                            # userprofile.save()
                            UserCSV.objects.create(user=user, csv=event)
                            successMessage = "%s is purchased successfully."%(event.name)
                            reload_window = "Reload"
                            # send_donation_email(tplVar, user.email)
                            # return HttpResponseRedirect('/account/')
                except Exception as e:
                    print 'here error 2: ', e
                    stripeError = "Your card was declined."
    content = {
        'form':form,
        'successMessage':successMessage,
        'is_customer':is_customer,
        'userprofile':userprofile,
        'stripeError':stripeError,
        'credit':credit,
        'credits':credits,
        'reload_window':reload_window,
        'event':event,
    }
    return render(request,'iFrame/buy_event_iframe.html', content)


@login_required(login_url='/login/')
@staff_member_required
def invoices_data_purchase(request):
    user = request.user
    successMessage = None
    events_purchased = UserCSV.objects.select_related('csv').filter(user=user).order_by('created_at')[:4]
    events_purchased_list = events_purchased.values_list('csv__id', flat=True)
    events = csvUpload.objects.all().exclude(id__in=events_purchased_list).order_by('created_at')
    form = csvform()
    message = None
    if request.method == "POST":
        form = csvform(request.POST, request.FILES)
        if form.is_valid():
            # 'name','csv','is_visible'
            print "form is valid"
            data = form.cleaned_data
            print data
            # form.csv.save()
            # form.save()
            name = request.FILES['csv'].name
            file = request.FILES['csv']
            sub = request.POST['name']
            is_visible = request.POST['is_visible']
            csv_obj = csvUpload.objects.create(name=sub, csv=file, is_visible=is_visible)
            print name
            download_file('%sstatic/%s'%(MEDIA_URL, name))
            save_file(name)
            print 'file is saved'
            print 'opening the file'
            objects = []
            with open(name, 'rU') as f:
                print "script started"
                reader = csv.reader(f)
                next(reader, None)
                mylist = []

                'starting the row'
                for row in reader:
                    first_name = row[0]
                    last_name = row[1]
                    email = row[2]
                    phone = row[3]
                    city = row[4]
                    state = row[5]
                    zip = row[6]
                    wedding_date = row[7]
                    print first_name, last_name, email, phone, city, state, zip, wedding_date

                    objects.append(csvData(csv=csv_obj,
                                           first_name=first_name,
                                           last_name=last_name,
                                           email=email,
                                           phone=phone,
                                           city=city,
                                           state=state,
                                           zip=zip,
                                           wedding_date=wedding_date))
                csvData.objects.bulk_create(objects)
                csv_obj.csv.delete()
                successMessage = "CSV is uploaded successfully."
    print events
    return render(request, 'vendroid/CRM/data_list_purchase.html', {
        'events':events,
        'events_purchased':events_purchased,
        'form':form,
        'successMessage':successMessage,
    })

import requests
import os
import shutil

global dump
def download_file(url):
    global dump
    file = requests.get(url, stream=True)
    dump = file.raw

def save_file(name):
    global dump
    location = os.path.abspath(BASE_DIR)
    with open(name, 'wb') as location:
        shutil.copyfileobj(dump, location)
    del dump

@login_required(login_url='/login/')
@staff_member_required
def event_invoice_detail(request, id):
    user = request.user
    invoices = None
    try:
        invoices = Invoice_Event.objects.filter(registered_event_id=id, user=user)
    except Exception as e:
        print e
        raise Http404
    print invoices
    return render(request, 'vendroid/CRM/invoices_detail.html', {
        'invoices':invoices,
        'id':id,
    })

@login_required(login_url='/login/')
@staff_member_required
def event_invoice_edit_detail(request, id):
    user = request.user
    invoices = None
    invoice = None
    initial = {}
    try:
        invoices = Invoice_Event.objects.get(id=id, user=user)
        invoice = invoices.registered_event
        initial = {
            'prize':invoices.prize,
            'notes':invoices.notes,
            'amount':invoices.amount,
            'is_sent':invoices.is_sent,
        }
    except Exception as e:
        print e
        raise Http404
    form = InvoiceCreationForm(initial=initial)
    if request.method == "POST":
        form = InvoiceCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            amount = data['amount']
            prize = data['prize']
            notes = data['notes']
            is_sent = data['is_sent']
            invoices.amount = amount
            invoices.prize = prize
            invoices.notes = notes
            invoices.is_sent = is_sent
            invoices.save()
            return HttpResponseRedirect('/crm/invoices/detail/%s'%(invoice.id))

    print invoices
    return render(request, 'vendroid/CRM/edit_invoice.html', {
        'invoices':invoices,
        'invoice':invoice,
        'id':id,
        'form':form,
    })

from django.contrib.auth import authenticate, logout, login as auth_login
@login_required(login_url='/login/')
@staff_member_required
def crm_view_agreement(request, code):
    user = request.user
    invoices = None
    try:
        agreement = Register_Event_Aggrement.objects.get(code=code)
        invoices = agreement.register_event
        # print invoices.registered_event.email
        user = User.objects.get(username=invoices.email)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect('/crm/view/complete/agreement/%s'%(agreement.code))
    except Exception as e:
        print e
        raise Http404
    return render(request, 'vendroid/CRM/invoices_detail.html', {
        'invoices':invoices,
        'code':code,
    })


def crm_view_complete_agreement(request, code):
    print code
    agreement = get_object_or_404(Register_Event_Aggrement, code=code)
    if not agreement.status == Register_Event_Aggrement.VIEWED and not agreement.status == Register_Event_Aggrement.ACCEPTED and not agreement.status == Register_Event_Aggrement.REJECTED :
        agreement.status = Register_Event_Aggrement.VIEWED
        agreement.save()
        context = {
                    'message':"User with email %s has viewed the invoice with id: %s."%(agreement.email, agreement.id),
                    'title':"Viewed: Bay Area Wedding Fairs Invoice",
                    }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Viewed", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com','adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        message = "Invoice request sent successfully."
    if "accept" in request.POST:
        agreement.status = Register_Event_Aggrement.ACCEPTED
        agreement.save()
        context = {
                    'message':"User with email %s has accepted the invoice with id: %s."%(agreement.email, agreement.id),
                    'title':"Accepted: Bay Area Wedding Fairs Invoice",
                    }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com','adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        context = {
                    'message':"Thank you for accepting the agreement no %s with BayAreaWeddingFairs, You will be sent an invoice shortly for the event. <br /><br />Kindly get back to us with an email, or the reply to this email if you have not initiated the above action."%(agreement.id),
                    'title':"Accepted: Bay Area Wedding Fairs Invoice",
                    }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,from_email='info@bayareaweddingfairs.com',to=[agreement.email], cc=['info@bayareaweddingfairs.com','adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    if "decline" in request.POST:
        agreement.status = Register_Event_Aggrement.REJECTED
        agreement.save()
        context = {
                    'message':"User with email %s has rejected the invoice with id: %s."%(agreement.email, agreement.id),
                    'title':"Rejected: Bay Area Wedding Fairs Invoice",
                    }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Rejected", text_content, 'info@bayareaweddingfairs.com', ['info@bayareaweddingfairs.com','adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    notes = None
    # invoices = agreement.invoices
    # if invoices:
    #     pass
        # notes = Notes.objects.filter(exhibitor__id=invoices[0].register)
    invoices = agreement.invoices.all()
    inv = None
    reg = None
    notes = None
    if invoices:
        inv = invoices[0]
        reg = invoices[0].register
        notes = Notes.objects.filter(exhibitor=reg)

    return render(request, 'vendroid/CRM/agreement.html',{
        'agreement':agreement,
        'invoices':invoices,
        'notes':notes,
        'inv':inv,
        'reg':reg,
        'notes':notes,
    })

from django.contrib.auth import authenticate, logout, login as auth_login
@login_required(login_url='/login/')
@staff_member_required
def event_invoice_accept(request, code):
    user = request.user
    invoices = None
    try:

        invoices = EventInvoiceRequest.objects.get(code=code)
        # print invoices.registered_event.email
        user = User.objects.get(username=invoices.event_invoice.email)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect('/invoices/pay/%s/'%(invoices.id))
    except Exception as e:
        print e
        raise Http404
    print invoices
    return render(request, 'vendroid/CRM/invoices_detail.html', {
        'invoices':invoices,
        'code':code,
    })


@login_required(login_url='/login/')
@staff_member_required
def event_invoice_accept_bulk(request, code):
    user = request.user
    invoices = None
    try:
        invoices = BulkInvoices.objects.get(code=code)
        print invoices.email
        user = User.objects.get(username=invoices.email)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect('/invoices/?invoice_id_bulk=%s'%(invoices.id))
    except Exception as e:
        print e
        raise Http404
    print invoices
    return render(request, 'vendroid/CRM/invoices_detail.html', {
        'invoices':invoices,
        'code':code,
    })



import stripe
@login_required(login_url='/login/')
@staff_member_required
def event_invoice_pay(request, id):
    user = request.user
    profile = user.userprofile
    invoice = None
    event = None
    company = profile.userprofile_company
    form = CreditCardForm()
    try:
        invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, user=user)
        event = invoice.registered_event.event
    except Exception as e:
        print e
        raise Http404
    print invoice
    if request.method == "POST":
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = "sk_live_n8WrsUoKt0Esb2cfUAIBHWgn"
            token = request.POST.get('stripe_token')
            customer = stripe.Customer.create(email=invoice.registered_event.email,

                                              source=token)
            charge = stripe.Charge.create(
                                            amount=(invoice.amount*100), # in cents
                                            currency="usd",
                                            customer=customer.id)
            invoice.payment_date = datetime.now().date()
            invoice.transaction_id = charge.stripe_id
            invoice.status = Invoice_Event.PAID
            invoice.save()

    today = datetime.now().date()
    return render(request, 'vendroid/CRM/invoice_pay.html', {
        'invoice':invoice,
        'today':today,
        'profile':profile,
        'company':company,
        'form':form,
        'event':event,
    })



import stripe
@login_required(login_url='/login/')
@staff_member_required
def event_invoice_deposit_pay(request, id, code):
    user = request.user
    profile = user.userprofile
    invoice = None
    event = None
    company = profile.userprofile_company
    form = CreditCardForm()
    try:
        invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, user=user)
        event = invoice.registered_event.event
    except Exception as e:
        print e
        raise Http404
    print invoice
    if request.method == "POST":
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = "sk_live_n8WrsUoKt0Esb2cfUAIBHWgn"
            token = request.POST.get('stripe_token')
            customer = stripe.Customer.create(email=invoice.registered_event.email,

                                              source=token)
            charge = stripe.Charge.create(
                                            amount=(invoice.amount*100), # in cents
                                            currency="usd",
                                            customer=customer.id)
            invoice.payment_date = datetime.now().date()
            invoice.transaction_id = charge.stripe_id
            invoice.status = Invoice_Event.PAID
            invoice.save()

    today = datetime.now().date()

    print code
    agreement = get_object_or_404(Register_Event_Aggrement, code=code)
    if not agreement.status == Register_Event_Aggrement.VIEWED and not agreement.status == Register_Event_Aggrement.ACCEPTED and not agreement.status == Register_Event_Aggrement.REJECTED:
        agreement.status = Register_Event_Aggrement.VIEWED
        agreement.save()
        context = {
            'message': "User with email %s has viewed the invoice with id: %s." % (agreement.email, agreement.id),
            'title': "Viewed: Bay Area Wedding Fairs Invoice",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Viewed", text_content,
                                     'info@bayareaweddingfairs.com',
                                     ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        message = "Invoice request sent successfully."
    if "accept" in request.POST:
        agreement.status = Register_Event_Aggrement.ACCEPTED
        agreement.save()
        context = {
            'message': "User with email %s has accepted the invoice with id: %s." % (agreement.email, agreement.id),
            'title': "Accepted: Bay Area Wedding Fairs Invoice",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                     'info@bayareaweddingfairs.com',
                                     ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        context = {
            'message': "Thank you for accepting the agreement no %s with BayAreaWeddingFairs, You will be sent an invoice shortly for the event. <br /><br />Kindly get back to us with an email, or the reply to this email if you have not initiated the above action." % (
            agreement.id),
            'title': "Accepted: Bay Area Wedding Fairs Invoice",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                     from_email='info@bayareaweddingfairs.com', to=[agreement.email],
                                     cc=['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    if "decline" in request.POST:
        agreement.status = Register_Event_Aggrement.REJECTED
        agreement.save()
        context = {
            'message': "User with email %s has rejected the invoice with id: %s." % (agreement.email, agreement.id),
            'title': "Rejected: Bay Area Wedding Fairs Invoice",
        }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Rejected", text_content,
                                     'info@bayareaweddingfairs.com',
                                     ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    notes = None
    # invoices = agreement.invoices
    # if invoices:
    #     pass
    # notes = Notes.objects.filter(exhibitor__id=invoices[0].register)
    invoices = agreement.invoices.all()
    inv = None
    reg = None
    notes = None
    if invoices:
        inv = invoices[0]
        reg = invoices[0].register
        notes = Notes.objects.filter(exhibitor=reg)

    return render(request, 'vendroid/CRM/invoice_pay.html', {
        'invoice':invoice,
        'today':today,
        'profile':profile,
        'company':company,
        'form':form,
        'event':event,
        'agreement': agreement,
        'invoices': invoices,
        'notes': notes,
        'inv': inv,
        'reg': reg,
        'notes': notes,
    })




@login_required(login_url='/login/')
@staff_member_required
def event_invoice_pay_bulk(request, id):
    user = request.user
    profile = user.userprofile
    invoice = None
    event = None
    company = profile.userprofile_company
    form = CreditCardForm()
    try:
        invoice = BulkInvoices.objects.get(id=id)
        # event = invoice.invoice_event.all()[0].registered_event.event
        # if not invoice.is_signed:
        #     return HttpResponseRedirect('/invoices/bulk/')
    except Exception as e:
        print e
        raise Http404
    print invoice
    if request.method == "POST":
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = "sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt"
            token = request.POST.get('stripe_token')
            customer = stripe.Customer.create(email=invoice.email,

                                              source=token)
            charge = stripe.Charge.create(
                                            amount=(int(invoice.get_amount())*100), # in cents
                                            currency="usd",
                                            customer=customer.id)
            # for o in invoice.invoice_event_vendor.all():
            #     o.payment_date = datetime.now().date()
            #     o.transaction_id = charge.stripe_id
            #     o.status = InvoiceRegisterVendor.PAID
            #     o.save()
            invoice.payment_date = datetime.now().date()
            invoice.status = Invoice_Event.PAID
            invoice.save()

    today = datetime.now().date()
    return render(request, 'vendroid/CRM/invoices_pay_bulk.html', {
        'invoice':invoice,
        'today':today,
        'profile':profile,
        'company':company,
        'form':form,
        'event':event,
    })


@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def invoice(request):
    user = request.user
    profile = user.userprofile
    content = {
    }

    template_name = 'vendroid/CRM/invoice.html'
    return render(request, template_name, content)

from django.shortcuts import HttpResponse
from django.template import RequestContext, loader
@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def FileLoading(request):
    #For administrators only
    #Must be superuser
    csvform = UserInfoForm()

    req_user = request.user
    if req_user.is_superuser:
        wp = UserProfile.objects.filter(type=UserProfile.PROFESSIONAL)
        events = HostEvent.objects.all()

        #Load CSV File
        if "csvFile" in request.POST or "csvFile" in request.FILES:
            print 'inside csvFile'
            userinfo_form = UserInfoForm(request.POST, request.FILES)
            print userinfo_form

            event_id = 0
            if userinfo_form.is_valid():
                csvFile = userinfo_form.cleaned_data['csvFile']
                file_url = MEDIA_URL+'media/'+str(csvFile)
                print "file_url is "+str(file_url)

                try:
                    host_event = HostEvent.objects.get(id=event_id)
                except:
                    host_event = []

                try:
                    csv_model = CSVFile.objects.get(csvfile='media/'+str(csvFile))
                    print "get csv already there"
                except:
                    print "create csv there"
                    csv_model = CSVFile.objects.create(csvfile=csvFile, hostevent=host_event)
                    #store to S3
                    out = csv_model.csvfile.storage
                    read_csv_from_url(csvFile, csv_model.id)

        elif "select_wp" in request.POST:
            wp_id = request.POST.get('select_wp')
            print "wp id "+str(wp_id)
            try:
                wp_name = UserProfile.objects.get(id=wp_id).user.get_full_name()
            except:
                wp_name = ""

            print "name "+str(wp_name)
            content = {
                 'wp_name': wp_name,
            }
            return JsonResponse(content, safe=False)

        elif "select_event" in request.POST:
            event_id = request.POST.get('select_event')
            print "event_id "+str(event_id)
            try:
                event_name = HostEvent.objects.get(id=event_id).subject
            except:
                event_name = ""

            print "event name "+str(event_name)
            content = {
                 'event_name': event_name,
            }
            return JsonResponse(content, safe=False)

        content = {
            'wps': wp,
            'events': events,
            'csvform': csvform,
        }

        template_name = 'vendroid/CRM/FileLoad.html'

        return render(request, template_name, content)

    else:
        warning = "Sorry, you must be the Administrator to view this page."
        content = {
            'warning': warning
        }
        template_name = "vendroid/superuser.html"
        return render(request, template_name, content)

#For administrators only
@login_required(login_url='/login/')
@csrf_exempt
def CreateEvent(request):
    #Must be superuser

    req_user = request.user
    if req_user.is_superuser:
        #Fix me
        # hostevent = HostEvent.objects.create()
        # content = {
        #     'event':hostevent
        # }

        template_name = 'vendroid/CRM/HostEvent.html'
        # return render(request, template_name, content)
        return render(request, template_name)

    else:
        template_name = "vendroid/CRM/superuser.html"
        return render(request, template_name)


#For administrators only
from django.contrib import messages
@login_required(login_url='/login/')
@csrf_exempt
def CreateWpForm(request):
    #Must be superuser
    req_user = request.user

    if req_user.is_superuser:
        wpForm = WpInfoForm()
        events = HostEvent.objects.all()

        if request.method == "POST":
            # print 'inside wp form'
            wpinfoForm = WpInfoForm(request.POST)

            if wpinfoForm.is_valid():
                # print "get into form"
                firstname = wpinfoForm.cleaned_data['firstname']
                lastname = wpinfoForm.cleaned_data['lastname']
                date = wpinfoForm.cleaned_data['date']
                # event_id = wpinfoForm.cleaned_data['event']
                email = wpinfoForm.cleaned_data['email']
                amount = wpinfoForm.cleaned_data['amount']

                #deal with event
                event_id = request.POST.get('events_to')
                # print "event_id "+str(event_id)

                try:
                    event = HostEvent.objects.get(id=event_id)
                except:
                    event = []

                print "email is "+str(email)

                try:
                    wp = WpInfo.objects.get(email=email)
                    # feedback = "fail"
                    print "already exist wp email "+str(email)

                except:
                    wp = WpInfo.objects.create(firstname=firstname,
                                               lastname=lastname,
                                               date=date,
                                               event=event,
                                               email=email,
                                               amount=amount)
                    # feedback = "success"
                    print "created wp model "+str(email)

                return HttpResponseRedirect("/crm/createWpform/")
            else:
                print "form not valid"
                messages.error(request, "form submission failed")
            # else:
            #     print "form not valid"


        content = {
            'events': events,
            'WpForm': wpForm,
        }

        #Create the form
        template_name = 'vendroid/CRM/wpForm.html'
        return render(request, template_name, content)

    else:
        #for normal users
        warning = "Sorry, you must be the Administrator to view this page."
        content = {
            'warning': warning
        }
        template_name = "vendroid/superuser.html"
        return render(request, template_name, content)



@login_required(login_url='/login/')
def Wizard_st1(request, email):
    form = None
    form = InvoiceForm_BulkCreate(email=email)
    content = {
        'form':form,
    }
    return render(request,'vendroid/CRM/iFrame/Wizard_st1.html', content)

@login_required(login_url='/crm/login/')
@csrf_exempt
def ViewWpForm(request):
    req_user = request.user

    print "view wp form"
    if req_user.userprofile.type == UserProfile.PROFESSIONAL:
        print "is wp"
        #for wedding professionals

        try:
            wpinfo = WpInfo.objects.get(email=req_user.email)
            initial = {
                'firstname':wpinfo.firstname,
                'lastname':wpinfo.lastname,
                'email':wpinfo.email,
                'date':wpinfo.date,
                'amount':wpinfo.amount,
            }
            WpForm = WpInfoForm(initial=initial)
            event_name = wpinfo.event.subject
            print "have form"
        except:
            WpForm = []
            wpinfo = []
            event_name = ''

        if "wpForm" in request.POST:
            wpinfoForm = WpInfoForm(request.POST)
            # print wpinfoForm

            if wpinfoForm.is_valid():
                accept = wpinfoForm.cleaned_data['accept']

                if accept == True:
                    try:
                        wpinfo.accepted = True
                        wpinfo.save()
                        feedback = "success"

                    except:
                        feedback = "fail"
                else:
                    feedback = "not accepted"
            else:
                feedback = "not valid"

            content = {
                'feedback': feedback
            }
            return JsonResponse(content, safe=False)

        content = {
            'WpForm': WpForm,
            'event_name': event_name
        }

        #view form
        template_name = 'vendroid/CRM/wpForm.html'
        return render(request, template_name, content)

    else:
        #for normal users
        warning = "Sorry, you must be the Administrator or Wedding Professional to view this page."
        content = {
            'warning': warning
        }
        template_name = "vendroid/superuser.html"
        return render(request, template_name, content)

@login_required(login_url="/crm/login/")
@staff_member_required
@csrf_exempt
def interested_contractor(request):
    user = request.user
    view_all = None
    email_sent = None
    initial_word = ""
    events = None#Register_Event_Interested.objects.select_related('user').filter( ~Q(type=Register_Event_Interested.BGUSER)).order_by('-created_at')
    salesCandidates = User.objects.filter(is_superuser=True)
    # if request.is_ajax():
    #     search = request.POST.get('search')
    #     print search
    #     if search:
    #         print 'inside search'
    #         try:
    #             initial_word = search
    #             search = search.split(' ')[0]
    #             userprofile = UserProfile.objects.get(user__email=search)
    #             return HttpResponse('success')
    #         except Exception as e:
    #             print e
    #             return HttpResponse('failed')
    #     else:
    #         print 'inside search else'
    #         return HttpResponse('failed')
    if request.method == 'POST':
        if 'search' in request.POST:
            print 'inside search'
            search = request.POST.get('search')
            try:
                initial_word = search
                search = search.split(' ')[0]
                print 'search email: ',search
                if search:
                    userprofile = UserProfile.objects.get(user__email__iexact=search)
                    name = userprofile.user.get_full_name()
                    if not name:
                        name = "N/A"
                    Register_Event_Interested.objects.create(user=userprofile.user,
                                                             name=name,
                                                             business_name=userprofile.userprofile_company.name,
                                                             phone=userprofile.phone,
                                                             email=userprofile.user.email,
                                                             city=userprofile.city,
                                                             zip=userprofile.zip
                                                             )
                    return HttpResponseRedirect('')
            except Exception as e:
                print "Exception in IV search: ",e
        elif 'search2' in request.POST:
            print 'inside search 2'
            try:
                search = request.POST.get('search2')
                initial_word = search
                search = search.split(' ')[0]
                events = Register_Event_Interested.objects.select_related('user').filter(
                    ~Q(type=Register_Event_Interested.BGUSER)).filter(email__icontains=search).exclude(status=Register_Event_Interested.REMOVED).order_by('-created_at')
            except Exception as e:
                print e
                # return HttpResponseRedirect('')
        elif "export_all" in request.POST:
            print 'viewpost'
            output = []
            # event_selected = request.POST.get('csv_export_all', None)
            # csv_export_id = request.POST.get('csv_export_id', None)
            # print 'csv_export_all: ', event_selected, csv_export_id
            response = HttpResponse(content_type='text/CSV')
            response['Content-Disposition'] = 'attachment;filename=export.csv'
            # response.ContentType = "application/CSV";
            # response.AddHeader("Content-Disposition", "attachment;records.csv");
            writer = csv.writer(response)
            search_list = []
            query_set = []
            query_set = Register_Event_Interested.objects.filter(email__isnull=False).exclude(status=Register_Event.REMOVED)#.order_by('-created_at')
            print 'query set: ', query_set
            import unicodedata
            if query_set:
                print 'In query set: ', query_set.count()
                writer.writerow(
                    ['Vendors Name', 'Company Name','Email', 'Created At'])
                for data in query_set:
                    name = "N/A"
                    if data.name:
                        name = unicodedata.normalize('NFKD', data.name).encode('ascii', 'ignore')
                    business_name = "N/A"
                    if data.business_name:
                        business_name = unicodedata.normalize('NFKD', data.business_name).encode('ascii', 'ignore')
                    email = "N/A"
                    if data.email:
                        email = unicodedata.normalize('NFKD', data.email).encode('ascii', 'ignore')
                    # name = "N/A"
                    # if data.name:
                    #     name = unicodedata.normalize('NFKD', data.name).encode('ascii', 'ignore')

                    # unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
                    # 'first_name','last_name','user__email','amount','frequency','donate_as','phone','occupation','address','city','state','zip'
                    output.append([name, business_name, email, str(data.created_at)])
                writer.writerows(output)
                return response
        else:
            events = Register_Event_Interested.objects.select_related('user').all().filter(
                ~Q(type=Register_Event_Interested.BGUSER)).exclude(status=Register_Event_Interested.REMOVED).order_by('-created_at')
    else:
        events = Register_Event_Interested.objects.select_related('user').all().filter(
            ~Q(type=Register_Event_Interested.BGUSER)).exclude(status=Register_Event_Interested.REMOVED).order_by('-created_at')
    # print events
    if "viewall" in request.POST:
        view_all = True
    elif "view_my_leads" in request.POST:
        events = events.filter(sales=user)
    return render(request, 'vendroid/CRM/interested_vendors.html', {
        'events':events,
        'view_all':view_all,
        'email_sent':email_sent,
        'initial_word':initial_word,
        'salesCandidates':salesCandidates,
    })


@login_required(login_url="/login/")
@staff_member_required
@csrf_exempt
def events_based_list_bg(request):
    # user = request.user
    email_sent = None
    csv_export_id = None
    form = events_search_form()
    events = None
    event_selected = None
    last_year = []
    this_year = []
    next_year = []
    events_all = Event_fairs.objects.all().order_by('-date')
    this_year_no = datetime.now().date().year
    last_year_no = this_year_no - 1
    next_year_no = this_year_no + 1
    for e in events_all:
        if e.date.year == this_year_no:
            this_year.append(e)
        elif e.date.year == last_year_no:
            last_year.append(e)
        elif e.date.year == next_year_no:
            next_year.append(e)
    if 'csv_export_all' in request.POST:
        output = []
        event_selected = request.POST.get('csv_export_all', None)
        csv_export_id = request.POST.get('csv_export_id', None)
        print 'csv_export_all: ',event_selected, csv_export_id
        response = HttpResponse(content_type='text/CSV')
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        # response.ContentType = "application/CSV";
        # response.AddHeader("Content-Disposition", "attachment;records.csv");
        writer = csv.writer(response)
        search_list = []
        query_set = []
        if not csv_export_id == "None":
            print 'inside if: ',csv_export_id
            if csv_export_id == "lastyear":
                print 'in last year: ',last_year
                search_list = last_year
            elif csv_export_id == "thisyear":
                print 'in this year'
                search_list = this_year
            elif csv_export_id == "nextyear":
                print 'in next year'
                search_list = next_year
            query_set = Register_Event.objects.select_related('event', 'sales').filter(type=Register_Event.BGUSER).filter(
            event__in=search_list).exclude(status=Register_Event.REMOVED).order_by('-created_at')
        elif event_selected:
            print 'inside else'
            query_set = Register_Event.objects.select_related('event').filter(type=Register_Event.BGUSER).filter(event_id=event_selected).exclude(status=Register_Event.REMOVED).order_by('-created_at')
        print 'query set: ',query_set
        if query_set:
            print 'In query set: ',query_set.count()
            writer.writerow(['Bride Name','Email','City','Zip','Phone','Wedding Date','How Heard','Wedding Professional Interested in','Comments','Show','Created At'])
            for data in query_set:
                print [data.name, data.email,data.city,data.zip, data.phone, data.weddingDate, data.how_heard, ["".join("%s "%(str(x.category))) for x in data.categories.all()],data.comments ,"%s - %s"%(data.event.name, data.event.date), data.created_at]
                cat = ""
                for c in data.categories.all():
                    cat += "%s "%(c.category)
                # 'first_name','last_name','user__email','amount','frequency','donate_as','phone','occupation','address','city','state','zip'
                output.append([data.name, data.email,data.city,data.zip, data.phone, "%s"%(data.weddingDate.date() if data.weddingDate else 'N/A'), data.how_heard, cat,data.comments ,"%s - %s"%(data.event.name, data.event.date), data.created_at.date()])
            writer.writerows(output)
            return response


    if "events_year" in request.POST:
        events_year = request.POST.get('events_year')
        print 'search value: ',events_year
        search_list = []
        if events_year == "lastyear":
            print 'in last year'
            csv_export_id = "lastyear"
            search_list = last_year
        elif events_year == "thisyear":
            print 'in this year'
            csv_export_id = "thisyear"
            search_list = this_year
        elif events_year == "nextyear":
            print 'in next year'
            csv_export_id = "nextyear"
            search_list = next_year
        events = Register_Event.objects.select_related('event', 'sales').filter(type=Register_Event.BGUSER).filter(
            event__in=search_list).exclude(status=Register_Event.REMOVED).order_by('-created_at')
    elif request.method == 'POST':
        form = events_search_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            event_selected = data['events']
            events = Register_Event.objects.select_related('event','sales').filter(type=Register_Event.BGUSER).filter(event=event_selected).exclude(status=Register_Event.REMOVED).order_by('-created_at')



    # print this_year, last_year, next_year
    return render(request, 'vendroid/CRM/event_search_bg.html', {
        'event_selected':event_selected,
        'events':events,
        'email_sent':email_sent,
        'form':form,
        'this_year':this_year,
        'this_year_no':this_year_no,
        'last_year':last_year,
        'last_year_no':last_year_no,
        'next_year':next_year,
        'next_year_no':next_year_no,
        'csv_export_id':csv_export_id,
        # 'staff':staff,
    })

@login_required(login_url="/login/")
@staff_member_required
@csrf_exempt
def events_based_list(request):
    # user = request.user
    print ("hfd")
    email_sent = None
    csv_export_id = None
    form = events_search_form()
    events = None
    event_selected = None
    last_year = []
    this_year = []
    next_year = []
    events_all = Event_fairs.objects.all().order_by('-date')
    this_year_no = datetime.now().date().year
    last_year_no = this_year_no - 1
    next_year_no = this_year_no + 1
    sum = 0
    for e in events_all:
        if e.date.year == this_year_no:
            this_year.append(e)
        elif e.date.year == last_year_no:
            last_year.append(e)
        elif e.date.year == next_year_no:
            next_year.append(e)
    if 'csv_export_all' in request.POST:
        output = []
        event_selected = request.POST.get('csv_export_all', None)
        csv_export_id = request.POST.get('csv_export_id', None)
        print 'csv_export_all: ',event_selected, csv_export_id
        response = HttpResponse(content_type='text/CSV')
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        # response.ContentType = "application/CSV";
        # response.AddHeader("Content-Disposition", "attachment;records.csv");
        writer = csv.writer(response)
        search_list = []
        query_set = []
        if not csv_export_id == "None":
            print 'inside if: ',csv_export_id
            if csv_export_id == "lastyear":
                print 'in last year: ',last_year
                search_list = last_year
            elif csv_export_id == "thisyear":
                print 'in this year'
                search_list = this_year
            elif csv_export_id == "nextyear":
                print 'in next year'
                search_list = next_year
            query_set = Register_Event.objects.select_related('event', 'sales').exclude(type=Register_Event.BGUSER).filter(
            event__in=search_list).exclude(status=Register_Event.REMOVED).order_by('-created_at')
        elif event_selected:
            print 'inside else'
            query_set = Register_Event.objects.select_related('event').exclude(type=Register_Event.BGUSER).filter(event_id=event_selected).exclude(status=Register_Event.REMOVED).order_by('-created_at')
        print 'query set: ',query_set
        if query_set:
            print 'In query set: ',query_set.count()
            writer.writerow(['Vendors Name','Category','Company Name','Show','Balance Due','Payment Method','Status','Created At','Email'])
            for data in query_set:
                # 'first_name','last_name','user__email','amount','frequency','donate_as','phone','occupation','address','city','state','zip'
                output.append([data.name,data.category, data.business_name, "%s - %s"%(data.event.name, data.event.date),str(data.amount_due), data.payment_method, data.status, data.created_at,data.email])
            writer.writerows(output)
            return response


    if "events_year" in request.POST:

        events_year = request.POST.get('events_year')
        print 'search value: ',events_year
        search_list = []
        if events_year == "lastyear":
            print 'in last year'
            csv_export_id = "lastyear"
            search_list = last_year
        elif events_year == "thisyear":
            print 'in this year'
            csv_export_id = "thisyear"
            search_list = this_year
        elif events_year == "nextyear":
            print 'in next year'
            csv_export_id = "nextyear"
            search_list = next_year
        events = Register_Event.objects.select_related('event', 'sales').exclude(type=Register_Event.BGUSER).filter(
            event__in=search_list).exclude(status=Register_Event.REMOVED).order_by('-created_at')
    elif request.method == 'POST':
        print ("Search heree")
        form = events_search_form(request.POST)
        event_dict = {}
        event_list = []
        if form.is_valid():
            data = form.cleaned_data
            event_selected = data['events']
            print ("event: ", event_selected)
            events = Register_Event.objects.select_related('event','sales').exclude(type=Register_Event.BGUSER).filter(event=event_selected).exclude(status=Register_Event.REMOVED).order_by('-created_at')
            print (events.query)
            for e in events:
                print ('s: ', e.grand_prize)
                if e.grand_prize != None and e.grand_prize != '':
                    sum = sum + int(e.grand_prize)
            print ("i: ", sum)

            electricity = InvoiceRegisterVendor.objects.filter(register=events)
            print ("elec: ", electricity)

            for e in events:

                electricity = InvoiceRegisterVendor.objects.filter(register__id=e.event_id)

                print("elect: ", e.id, electricity)
                for el in electricity:
                    event_list.append({
                        'name':e.name,
                        'email':e.email,
                        'business_name':e.business_name,
                        'is_partner_vendor':e.is_partner_vendor,
                        'total_amount':e.total_amount,
                        'amount_due':e.amount_due,
                        'commission':e.commission,
                        'get_percent_amount':e.get_percent_amount,
                        'payment_method':e.payment_method,
                        'grand_prize':e.grand_prize,
                        'booth':e.booth,
                        'electricity':el.electricity_types,
                        'status':e.status,
                        'created_at':e.created_at

                    })

            # sum = Register_Event.objects.select_related('event','sales').exclude(type=Register_Event.BGUSER).filter\
            #     (event=event_selected).exclude(status=Register_Event.REMOVED).order_by('-created_at').aggregate(Sum(int('grand_prize') if ('grand_prize') else None)).get('grand_prize__sum', 0.00)

            print ("list: ", event_list)
    # print this_year, last_year, next_year
    return render(request, 'vendroid/CRM/event_search.html', {
        'event_selected':event_selected,
        'events':events,
        'email_sent':email_sent,
        'form':form,
        'this_year':this_year,
        'this_year_no':this_year_no,
        'last_year':last_year,
        'last_year_no':last_year_no,
        'next_year':next_year,
        'next_year_no':next_year_no,
        'csv_export_id':csv_export_id,
        'sum':sum
        # 'staff':staff,
    })

from django.db.models import Sum
@login_required(login_url="/login/")
@staff_member_required
@csrf_exempt
def commission(request):
    # user = request.user
    email_sent = None
    csv_export_id = None
    form = events_search_form()
    events = None
    event_selected = None
    # SalesCommission object
    staff_value = 0
    if "staff_value" in request.POST:
        staff_value = request.POST.get('staff_value')
        print 'inside staff id: ',staff_value
        events = Register_Event.objects.select_related('event', 'sales','sales_commission').filter(sales_id=staff_value).exclude(type=Register_Event.BGUSER).exclude(status=Register_Event.REMOVED).order_by('-created_at')
    elif "mark_paid_checkbox" in request.POST:
        mark_paid_checkbox = request.POST.getlist('mark_paid_checkbox')
        staff_value = request.POST.get('staff_value_retain')
        print "mark_paid_checkbox: ",mark_paid_checkbox

        events_marked = Register_Event.objects.filter(id__in=mark_paid_checkbox)
        amount = 0.0
        for o in events_marked:
            amount += o.get_percent_amount()
        comm = SalesCommission.objects.create(
            sales_id=staff_value,
            amount=amount,
            is_commission_paid=True,
            paid_by=request.user


        )
        for e in events_marked:
            e.is_commission_paid = True
            e.sales_commission = comm
            e.save()
        events = Register_Event.objects.select_related('event', 'sales','sales_commission').filter(sales_id=staff_value).exclude(
            type=Register_Event.BGUSER).exclude(status=Register_Event.REMOVED).order_by('-created_at')
    staff = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by('first_name')
    # print this_year, last_year, next_year
    return render(request, 'vendroid/CRM/commission.html', {
        'events':events,
        'staff':staff,
        'staff_value':int(staff_value),
    })



@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def interested_contractor_detail(request, id):
    user = request.user
    noteForm = contractor_detail_note_form()
    error_message = None
    wp = None

    show_form_errors = None
    initial = {
        'sales':request.user,
    }
    taskForm = sales_tasks_form(initial=initial)

    try:
        wp = Register_Event_Interested.objects.get(id=id)
    except Exception as e:
        print e
        raise Http404

    try: notes = NotesEx.objects.filter(exhibitor__id=id)
    except: notes = None
    # try: tasks = SalesTasks.objects.filter(exhibitor__id=id, sales=user)
    # except: tasks = None
    try: tasksComplete = SalesTasksEx.objects.filter(exhibitor__id=id, status=SalesTasksEx.COMPLETE)
    except: tasksComplete = None
    try: tasksInProgress = SalesTasksEx.objects.filter(exhibitor__id=id, status=SalesTasksEx.INPROGRESS)
    except: tasksInProgress = None

    try: sales = wp.sales
    except: sales = []
    Form = None
    if not request.POST:
        initial = {
            'event': wp.event,
            'user': wp.user,
            'name': wp.name,
            'phone': wp.phone,
            'email': wp.email,
            'city': wp.city,
            'zip': wp.zip,
            'business_name': wp.business_name,
            'comments': wp.comments,
            'how_heard': wp.how_heard,
            'categories': wp.category,
            'status': wp.status,
            'amount_due': wp.amount_due,
            'description': wp.description,
            'payment_method': wp.payment_method,
            'sales': sales,
            'website': wp.website,
            # 'commission': wp.commission,
        }


        Form = registration_event_form(initial=initial)
     # for the convert button
    if "convert" in request.POST:
        events_selected_id = request.POST.getlist('eventsCheck')
        print "1805: ",events_selected_id
        for events_id in events_selected_id:
            event_id_add = Event_fairs.objects.get(id=events_id)
            Register_Event.objects.create(
                event=event_id_add,
                user=wp.user,
                name=wp.name,
                business_name=wp.business_name,
                phone=wp.phone,
                email=wp.email,
                city=wp.city,
                zip=wp.zip,
                comments=wp.comments,
                type=wp.type,
                weddingDate=wp.weddingDate,
                how_heard=wp.how_heard,
                category=wp.category,
                status=Register_Event.UNPAID,
                amount_due=wp.amount_due,
                payment_method=wp.payment_method,
                description=wp.description,
                sales=wp.sales,
                is_lasVegasSignIn=wp.is_lasVegasSignIn,
                website=wp.website
            )
        wp.status = Register_Event_Interested.PAID
        wp.save()
        # print "change wp to unpaid vendor", wp.name, wp.status
        return HttpResponseRedirect("/crm/invoices/contracted/")

    elif request.POST.get("noteForm"):
        print "note form"
        getForm = contractor_detail_note_form(request.POST)

        # print getForm

        if getForm.is_valid():
            note = getForm.cleaned_data['note']
            # print wp.name, sales, note

            try: NotesEx.objects.create(exhibitor=wp, note=note, note_writer=user)
            except Exception as e:
                print e
                raise Http404

            print "create note form"
            return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
        else:
            print "form is not valid"
            error_message = "Please fill the Note"

    elif request.POST.get("taskForm"):
        print "task form"
        getForm = sales_tasks_form(request.POST)

        print getForm

        if getForm.is_valid():
            subject = getForm.cleaned_data['subject']
            message = getForm.cleaned_data['message']
            status = getForm.cleaned_data['status']
            dueDate = getForm.cleaned_data['dueDate']
            # sales = getForm.cleaned_data['sales']

            # print wp.name, sales, note

            try: SalesTasksEx.objects.create(
                subject=subject,
                message=message,
                status=status,
                dueDate=dueDate,
                sales=request.user,
                exhibitor=wp
            )
            except: raise Http404

            print "create note form"
            return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
        else:
            print "form is not valid"
            error_message = "Please fill the Task Form"

    #Retreive task info
    elif "assign_sales_person" in request.POST:
        assign_sales_person_2 = request.POST.get('assign_sales_person_2')
        print "sales person assign: ",assign_sales_person_2
        if assign_sales_person_2 != "None":
            wp.sales_id = assign_sales_person_2
            print "Done with sales"
        else:
            wp.sales_id = None
        wp.save()
        return HttpResponseRedirect('')
    elif request.is_ajax() and "editTaskForm" in request.POST:
        taskid = request.POST.get('editTaskForm')
        try:
            task = SalesTasksEx.objects.get(id=taskid)
            initial = {
                'subject': task.subject,
                'sales': task.sales,
                'exhibitor': task.exhibitor,
                'message': task.message,
                'dueDate': task.dueDate,
                'status':task.status,
                'modified_at':task.modified_at,
            }
            taskForm = sales_tasks_form(initial=initial)
        except: taskForm = sales_tasks_form()

        template = loader.get_template('vendroid/CRM/partial/_taskFromContractorDetailBody.html')
        content = {
             'error_message': error_message,
             'taskForm': taskForm,
             'taskid': taskid,
        }
        data = RequestContext(request, content)
        return HttpResponse(template.render(data))

    elif request.is_ajax() and "saveTaskFormID" in request.POST:
        print "save task form"
        print request.POST
        # getForm = sales_tasks_form(request.POST['saveTaskForm'])
        taskId = request.POST.get('saveTaskFormID')
        print taskId

        # # if getForm.is_valid():
        # subject = getForm.cleaned_data['subject']
        # message = getForm.cleaned_data['message']
        # status = getForm.cleaned_data['status']
        # dueDate = getForm.cleaned_data['dueDate']
        # sales = getForm.cleaned_data['sales']

        try:
            task = SalesTasksEx.objects.get(id=taskId)
            task.subject = request.POST.get('subject')
            task.message = request.POST.get('message')
            task.status = request.POST.get('status')
            task.dueDate = request.POST.get('dueDate')
            # task.sales_id = request.POST.get('sales')
            # task.exhibitor=wp
            task.save()
            print "save Task form"

            if request.POST.get('status') == SalesTasksEx.INPROGRESS:
                try: tasksComplete = SalesTasksEx.objects.filter(exhibitor__id=id, status=SalesTasksEx.COMPLETE)
                except: tasksComplete = None
            else:
                try: tasksInProgress = SalesTasksEx.objects.filter(exhibitor__id=id, status=SalesTasksEx.INPROGRESS)
                except: tasksInProgress = None


            return HttpResponse(json.dumps({
                'url':"/crm/invoices/interested_detail/%s/"%(id)
            }))

            # return render_to_redirect("vendroid/CRM/interested_contractors_details.html", {
            #     'wp': wp,
            #     'id':id,
            #     'is_contracted': False,
            #     'form': noteForm,
            #     'taskForm': taskForm,
            #     'notes':notes,
            #     'tasksComplete':tasksComplete,
            #     'tasksInProgress':tasksInProgress,
            #     'error_message': error_message,
            # }, context_instance=RequestContext(request))
            # return HttpResponse({
            #     'tasksComplete':tasksComplete,
            #     'tasksInProgress':tasksInProgress,
            # })

        except Exception as e:
            print e
            raise Http404


        # else:
        #     print "Task form is not valid"
        #     error_message = "Please fill the Task Form"

    #Retreive Register_event contract info and edit form
    elif request.is_ajax() and "editContractorForm" in request.POST:
        print "get here edit contractor"
        # wpID = request.POST.get('editContractorForm')
        try:
            print "id: ",id
            wp = Register_Event_Interested.objects.get(id=id)
            try: sales = wp.sales
            except: sales = None
            initial = {
                    'event': wp.event,
                    'user': wp.user,
                    'name': wp.name,
                    'phone': wp.phone,
                    'email': wp.email,
                    'city': wp.city,
                    'zip': wp.zip,
                    'business_name': wp.business_name,
                    'comments': wp.comments,
                    'how_heard': wp.how_heard,
                    'category': wp.category,
                    'categories': wp.category,
                    'status': wp.status,
                    'amount_due': wp.amount_due,
                    'description': wp.description,
                    'payment_method': wp.payment_method,
                    'sales': sales,
                    'website': wp.website,
                }
            print 'website: ',wp.website
            Form = registration_event_form(initial=initial)
        except Exception as e:
            print e
            raise Http404
        print "adding template"

        template = loader.get_template('vendroid/CRM/partial/_contractorDetail.html')
        content = {
             'error_message': error_message,
             'form': Form,
             'wp': wp,
        }
        data = RequestContext(request, content)
        return HttpResponse(template.render(data))

    #Save edited Register_event contract form
    elif request.POST.get("contratorForm"):
        # getForm = sales_tasks_form(request.POST)
        # print request.POST
        #
        # try:
        #     reg_wp = Register_Event.objects.get(id=id)
        #     reg_wp.category = request.POST['category']
        #     reg_wp.city = request.POST['city']
        #     reg_wp.name = request.POST['name']
        #     reg_wp.zip = request.POST['zip']
        #     reg_wp.how_heard = request.POST['how_heard']
        #     reg_wp.comments = request.POST['comments']
        #     reg_wp.phone = request.POST['phone']
        #     reg_wp.business_name = request.POST['business_name']
        #     reg_wp.email = request.POST['email']
        #     reg_wp.save()
        #
        #     print "saved new contract form"
        #     return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
        #
        # except: raise Http404



        Form = registration_event_form(request.POST)
        print 'inside reg event form'
        # data = form.cleaned_data
        # print data
        # print form

        if Form.is_valid():
            print 'form is valid'
            data = Form.cleaned_data
            print data

            try:
                reg_wp = Register_Event_Interested.objects.get(id=id)
            except Exception as e:
                print e
                reg_wp = []
                raise Http404

            reg_wp.name = data['name']
            reg_wp.business_name = data['business_name']
            reg_wp.phone = data['phone']
            reg_wp.email = data['email']
            reg_wp.city = data['city']
            reg_wp.zip = data['zip']
            reg_wp.comments = data['comments']
            reg_wp.how_heard = data['how_heard']
            reg_wp.category = data['category']
            reg_wp.booth = data['category']
            reg_wp.category = data['categories']
            print 'commission :',data['commission']
            reg_wp.commission = data['commission']
            reg_wp.website = data['website']
            reg_wp.save()

            print "saved new contract form"
            return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")

            # except: raise Http404

            # try:
            #     reg_wp = Register_Event.objects.get(id=id)
            #     reg_wp.category = request.POST['category']
            #     reg_wp.city = request.POST['city']
            #     reg_wp.name = request.POST['name']
            #     reg_wp.zip = request.POST['zip']
            #     reg_wp.how_heard = request.POST['how_heard']
            #     reg_wp.comments = request.POST['comments']
            #     reg_wp.phone = request.POST['phone']
            #     reg_wp.business_name = request.POST['business_name']
            #     reg_wp.email = request.POST['email']
            #     reg_wp.save()
            #
            #     print "saved new contract form"
            #     return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
            #
            # except: raise Http404


        else:
            print Form.errors
            print "Inside Else"
            # raise Http404
            show_form_errors = True
    #deal with change/assign sales
    elif request.is_ajax() and "chooseSales" in request.POST:
        salesID = request.POST.get('chooseSales')
        try:wp = Register_Event.objects.get(id=id)
        except: raise Http404

        try:
            sales = User.objects.get(id=salesID)
            wp.sales = sales
            wp.save()
        except:
            raise Http404

        content = {
            'sales': sales.get_full_name(),
        }
        return JsonResponse(content, safe=False)
    elif "edit_note_id" in request.POST:
        print 'inside edit notes id'
        edit_note_id = request.POST.get('edit_note_id')
        notes_to_edit = NotesEx.objects.get(id=edit_note_id)
        notes_to_edit.note = request.POST.get('note_text')
        notes_to_edit.save()
        return HttpResponseRedirect('')
    elif "remove_note_id" in request.POST:
        remove_note_id = request.POST.get('remove_note_id')
        note_to_delete = NotesEx.objects.get(id=remove_note_id).delete()
        return HttpResponseRedirect('')
    elif "delete_contractor" in request.POST:
        wp.status = Register_Event_Interested.REMOVED
        # wp.amount_due = wp.get_amount_due()
        # wp.total_amount = wp.get_amount_total()
        wp.save()
        return HttpResponseRedirect('/crm/invoices/interested/')
    staff = User.objects.filter(is_staff=True)
    events = Event_fairs.objects.filter(date__gte=datetime.now()).order_by('date')
    spring_events = []
    summer_events = []
    fall_events = []
    winter_events = []
    for event_chk in events:
        print "check 2474: ",event_chk.date
        season = choose_season(event_chk)
        # print event.name, event.date, event.date.month, season

        if season == 'Spring':
            spring_events.append(event_chk)
        elif season == 'Summer':
            summer_events.append(event_chk)
        elif season == 'Fall':
            fall_events.append(event_chk)
        elif season == 'Winter':
            winter_events.append(event_chk)
        else:
            print "Season is wrong", event_chk.date
    staff = User.objects.filter(is_staff=True)
    other_event = Event_fairs.objects.get(id=10)
    winter_events.append(other_event)

    return render(request, 'vendroid/CRM/interested_contractors_details.html', {
        'wp': wp,
        'id':id,
        'is_contracted': False,
        'form': noteForm,
        'taskForm': taskForm,
        'notes':notes,
        'tasksComplete':tasksComplete,
        'tasksInProgress':tasksInProgress,
        'error_message': error_message,
        'show_form_errors': show_form_errors,
        'show_interested': "True",
        'staff': "staff",
        'cont_form': Form,
        'events':Event_fairs.objects.filter(is_expired=False),
        'spring_events': spring_events,
        'summer_events': summer_events,
        'fall_events': fall_events,
        'winter_events': winter_events,
        'staff': staff,
    })

@login_required(login_url="/crm/login/")
@staff_member_required
@csrf_exempt
def contracted_contractor(request):
    # user = request.user
    # salesCandidates = User.objects.filter(is_superuser=True)
    wps = None
    view_all = None
    viewtype = None
    # wps = Register_Event.objects.filter(Q(status=Register_Event.PAID) & (~Q(type=Register_Event.BGUSER))).order_by('-created_at')
    initial_word = ""

    # print wps
    if 'search' in request.POST:
        search = request.POST.get('search')
        try:
            initial_word = search
            search = search.split(' ')[0]
            wps = Register_Event.objects.select_related('event').exclude(type=Register_Event.BGUSER).filter(
                email__icontains=search).exclude(status=Register_Event.REMOVED).order_by('-created_at')
            print('wps contracted: ', wps)
        except:
            pass

    else:
        wps = Register_Event.objects.select_related('event').all().exclude(type=Register_Event.BGUSER).exclude(status=Register_Event.REMOVED).order_by('-created_at')#[:10]
        print('wps contracted: else ', wps)
    # else:
    #     wps = Register_Event.objects.select_related('event').exclude(type=Register_Event.BGUSER).exclude(
    #         status=Register_Event.REMOVED).order_by('-created_at')
    if "viewtype" in request.POST:
        view_all = True
        viewtype = request.POST.get('viewtype')
        print 'viewtype: ',viewtype
        if viewtype == "paid":
            print 'mark paid'
            wps = wps.filter(total_amount__gt=0, amount_due=0)
        elif viewtype == "unpaid":
            print 'mark unpaid'
            wps = wps.filter(total_amount__gt=0, amount_due__gt=0)
    return render(request, 'vendroid/CRM/contracted_contractors.html', {
        'events':wps,
        'view_all':view_all,
        'viewtype':viewtype,
        'initial_word':initial_word,
        # 'salesCandidates':salesCandidates,
    })

@login_required(login_url='/crm/login/')
@staff_member_required
@csrf_exempt
def contracted_contractor_detail(request, id):
    pass_id = id
    user = request.user
    noteForm = contractor_detail_note_form()
    initial = {
        'sales':request.user,
    }
    taskForm = sales_tasks_form(initial=initial)
    error_message = None
    wp = None
    try:
        wp = Register_Event.objects.select_related('event','user','sales').get(id=id)
    except Exception as e:
        print e
        raise Http404

    print wp.name
    try: notes = Notes.objects.filter(exhibitor__id=id, note_writer=user)
    except: notes = None

    try: tasksComplete = SalesTasks.objects.filter(exhibitor__id=id, sales=user, status=SalesTasks.COMPLETE)
    except: tasksComplete = None

    try: tasksInProgress = SalesTasks.objects.filter(exhibitor__id=id, sales=user, status=SalesTasks.INPROGRESS)
    except: tasksInProgress = None

    try: sales = wp.sales
    except: sales = []
    Form = None
    if not request.POST:
        initial = {
            'event': wp.event,
            'user': wp.user,
            'name': wp.name,
            'phone': wp.phone,
            'email': wp.email,
            'city': wp.city,
            'zip': wp.zip,
            'business_name': wp.business_name,
            'comments': wp.comments,
            'how_heard': wp.how_heard,
            'categories': wp.category,
            'status': wp.status,
            'amount_due': wp.amount_due,
            'description': wp.description,
            'payment_method': wp.payment_method,
            'grand_prize': wp.grand_prize,
            'sales': sales,
            'commission': wp.commission,
            'booth': wp.booth,
            'food': wp.food,
            'is_fashionshow': wp.is_fashionshow,
            'is_partner_vendor': wp.is_partner_vendor,
            'backdrop_allowed': wp.backdrop_allowed,
            'website': wp.website,
        }
        Form = registration_event_form(initial=initial)
    invoice_form = InvoiceForm()
    message = None
    if "list_price" in request.POST:
        invoice_form = InvoiceForm(request.POST)
        if invoice_form.is_valid():
            data = invoice_form.cleaned_data
            list_price = data['list_price']
            offered_price = data['offered_price']
            pv_prize_offered = data['pv_prize_offered']
            payment_method = data['payment_method']
            electricity_types = data['electricity_types']
            email_list = data['email_list']
            inv = InvoiceRegisterVendor.objects.create(register=wp,
                                                       list_price=list_price,
                                                       offered_price=offered_price,
                                                       pv_prize_offered=pv_prize_offered,
                                                       # deposit=deposit,
                                                       # is_sent_deposit=send_email_now,
                                                       # balance1=balance1,
                                                       # balance2=balance2,
                                                       # balance3=balance3,
                                                       # date_balance1=date_balance1,
                                                       # date_balance2=date_balance2,
                                                       # date_balance3=date_balance3,
                                                       # date_deposit=date_deposit,
                                                       payment_method=payment_method,
                                                       electricity_types=electricity_types,
                                                       email_list=email_list,
                                                       )
            # wp.record_amount_due()
            wp.amount_due = wp.get_amount_due()
            wp.total_amount = wp.get_amount_total()
            wp.have_invoices += 1
            wp.save()
            message = "Invoice information added successfully."
            return HttpResponseRedirect("/crm/invoices/contracted_detail/" + id + "/")

    if "convert_back" in request.POST:
        wp.status = Register_Event.UNPAID
        wp.save()
        return HttpResponse("success")

    elif request.POST.get("noteForm"):
        print "note form interested"
        getForm = contractor_detail_note_form(request.POST)

        # print getForm

        if getForm.is_valid():
            note = getForm.cleaned_data['note']
            # print wp.name, sales, note

            try:
                print wp
                Notes.objects.create(exhibitor=wp, note_writer=request.user, note=note)
            except Exception as e:
                print "Notes exception",e
                raise Http404
            return HttpResponseRedirect("/crm/invoices/contracted_detail/"+id+"/")
        else:
            error_message = "Please fill the Note"
    elif request.POST.get("taskForm"):
        getForm = sales_tasks_form(request.POST)
        if getForm.is_valid():
            subject = getForm.cleaned_data['subject']
            message = getForm.cleaned_data['message']
            status = getForm.cleaned_data['status']
            dueDate = getForm.cleaned_data['dueDate']
            # sales = getForm.cleaned_data['sales']

            # print wp.name, sales, note

            try: SalesTasks.objects.create(
                subject=subject,
                message=message,
                status=status,
                dueDate=dueDate,
                sales=request.user,
                exhibitor=wp
            )
            except: raise Http404
            return HttpResponseRedirect("")
        else:
            print "form is not valid"
            error_message = "Please fill the Task Form"
    elif request.is_ajax() and "editTaskForm" in request.POST:
        taskid = request.POST.get('editTaskForm')
        try:
            task = SalesTasks.objects.get(id=taskid)
            initial = {
                'subject': task.subject,
                # 'sales': task.sales,
                'exhibitor': task.exhibitor,
                'message': task.message,
                'dueDate': task.dueDate,
                'status':task.status,
                'modified_at':task.modified_at,
            }
            taskForm = sales_tasks_form(initial=initial)
        except: taskForm = sales_tasks_form()

        template = loader.get_template('vendroid/CRM/partial/_taskFromContractorDetailBody.html')
        content = {
             'error_message': error_message,
             'taskForm': taskForm,
             'taskid': taskid,
        }
        data = RequestContext(request, content)
        return HttpResponse(template.render(data))

    elif request.is_ajax() and "saveTaskFormID" in request.POST:
        print "save task form submitted"
        print request.POST
        # getForm = sales_tasks_form(request.POST['saveTaskForm'])
        taskId = int(request.POST['saveTaskFormID'])
        print taskId

        # # if getForm.is_valid():
        # subject = getForm.cleaned_data['subject']
        # message = getForm.cleaned_data['message']
        # status = getForm.cleaned_data['status']
        # dueDate = getForm.cleaned_data['dueDate']
        # sales = getForm.cleaned_data['sales']

        try:
            task = SalesTasks.objects.get(id=taskId)
            task.subject = str(request.POST['subject'])
            task.message = str(request.POST['message'])
            task.status = str(request.POST['status'])
            task.dueDate = request.POST['dueDate']
            # task.sales_id = #int(request.POST['sales'])
            # task.exhibitor=wp
            task.save()
            print "save Task form done"

            if str(request.POST['status']) == SalesTasks.INPROGRESS:
                try: tasksComplete = SalesTasks.objects.filter(exhibitor__id=id, sales=user, status=SalesTasks.COMPLETE)
                except: tasksComplete = None
            else:
                try: tasksInProgress = SalesTasks.objects.filter(exhibitor__id=id, sales=user, status=SalesTasks.INPROGRESS)
                except: tasksInProgress = None
            print 'all success redirecting...'
            return HttpResponse('Success')
            if wp.type == Register_Event.CONTRACTOR:
                return HttpResponseRedirect("/crm/invoices/contracted_detail/" + id + "/")
            return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")

            # return render_to_redirect("vendroid/CRM/interested_contractors_details.html", {
            #     'wp': wp,
            #     'id':id,
            #     'is_contracted': False,
            #     'form': noteForm,
            #     'taskForm': taskForm,
            #     'notes':notes,
            #     'tasksComplete':tasksComplete,
            #     'tasksInProgress':tasksInProgress,
            #     'error_message': error_message,
            # }, context_instance=RequestContext(request))
            # return HttpResponse({
            #     'tasksComplete':tasksComplete,
            #     'tasksInProgress':tasksInProgress,
            # })

        except: raise Http404


        # else:
        #     print "Task form is not valid"
        #     error_message = "Please fill the Task Form"

    #Retreive Register_event contract info and edit form
    elif request.is_ajax() and "editContractorForm" in request.POST:
        print "edit contractor form"
        # wp = Register_Event.objects.get(id=id)
        # print wp.user

        try:
            wp = Register_Event.objects.get(id=id)
            try: sales = wp.sales
            except: sales = None
            initial = {
                    'event': wp.event,
                    'user': wp.user,
                    'name': wp.name,
                    'phone': wp.phone,
                    'email': wp.email,
                    'city': wp.city,
                    'zip': wp.zip,
                    'business_name': wp.business_name,
                    'comments': wp.comments,
                    'how_heard': wp.how_heard,
                    'categories': wp.category,
                    'status': wp.status,
                    'amount_due': wp.amount_due,
                    'description': wp.description,
                    'grand_prize': wp.grand_prize,
                    'payment_method': wp.payment_method,
                    'sales': sales,
                    'booth': wp.booth,
                    'is_fashionshow': wp.is_fashionshow,
                    'is_partner_vendor': wp.is_partner_vendor,
                    'backdrop_allowed': wp.backdrop_allowed,
                    'commission': wp.commission,
                    'food': wp.food,
                    'website': wp.website,
                }
            print "here"
            Form = registration_event_form(initial=initial)
            print "hhh"
        except:
            raise Http404

        template = loader.get_template('vendroid/CRM/partial/_contractorDetail.html')
        content = {
             # 'error_message': error_message,
             'form': Form,
        }
        data = RequestContext(request, content)
        return HttpResponse(template.render(data))

    #Save edited Register_event contract form
    elif request.POST.get("contratorForm"):
        # getForm = sales_tasks_form(request.POST)
        print request.POST
        #
        # try:
        #     reg_wp = Register_Event.objects.get(id=id)
        #     reg_wp.category = request.POST['category']
        #     reg_wp.city = request.POST['city']
        #     reg_wp.name = request.POST['name']
        #     reg_wp.zip = request.POST['zip']
        #     reg_wp.how_heard = request.POST['how_heard']
        #     reg_wp.comments = request.POST['comments']
        #     reg_wp.phone = request.POST['phone']
        #     reg_wp.business_name = request.POST['business_name']
        #     reg_wp.email = request.POST['email']
        #     reg_wp.save()
        #
        #     print "saved new contract form"
        #     return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
        #
        # except: raise Http404



        Form = registration_event_form(request.POST)
        print Form
        # data = form.cleaned_data
        # print data
        # print form

        if Form.is_valid():
            print 'form is valid'
            data = Form.cleaned_data
            print data

            try:
                reg_wp = Register_Event.objects.get(id=id)
            except:
                reg_wp = []
                raise Http404

            reg_wp.name = data['name']
            reg_wp.business_name = data['business_name']
            reg_wp.phone = data['phone']
            reg_wp.email = data['email']
            reg_wp.city = data['city']
            reg_wp.zip = data['zip']
            reg_wp.comments = data['comments']
            reg_wp.how_heard = data['how_heard']
            reg_wp.category = data['categories']
            reg_wp.booth = data['booth']
            reg_wp.food = data['food']
            reg_wp.is_fashionshow = data['is_fashionshow']
            reg_wp.is_partner_vendor = data['is_partner_vendor']
            reg_wp.backdrop_allowed = data['backdrop_allowed']
            reg_wp.website = data['website']
            reg_wp.grand_prize = data['grand_prize']
            print 'initial commission: ',wp.commission
            percent_amount = 0
            commission_percent = request.POST.get('select_commission')
            if commission_percent == 'other':
                commission_percent = data['commission']
            # if commission_percent:
            #     percent_amount = (float(reg_wp.total_amount)/100)*float(commission_percent)
            # print 'reg_wp.get_amount_total(): ',reg_wp.total_amount
            print 'percent_amount: ',percent_amount
            reg_wp.commission = float(commission_percent)
            print 'commission: ',data['commission']
            reg_wp.save()
            if reg_wp.booth == Register_Event.DELUXE:
                reg_wp.backdrop_allowed = True
                reg_wp.save()
            if reg_wp.booth == Register_Event.PREMIUM:
                reg_wp.backdrop_allowed = True
                reg_wp.save()

            for o in Register_Event.objects.filter(email__iexact=reg_wp.email):
                o.name = data['name']
                o.business_name = data['business_name']
                o.phone = data['phone']
                o.email = data['email']
                o.city = data['city']
                o.zip = data['zip']
                o.website = data['website']
                # o.comments = data['comments']
                # o.how_heard = data['how_heard']
                # o.category = data['category']
                # o.booth = data['booth']
                # o.is_fashionshow = data['is_fashionshow']
                # o.is_partner_vendor = data['is_partner_vendor']
                # o.backdrop_allowed = data['backdrop_allowed']
                o.save()

            print "saved new contract form"
            return HttpResponseRedirect("/crm/invoices/contracted_detail/"+id+"/")

            # except: raise Http404

            # try:
            #     reg_wp = Register_Event.objects.get(id=id)
            #     reg_wp.category = request.POST['category']
            #     reg_wp.city = request.POST['city']
            #     reg_wp.name = request.POST['name']
            #     reg_wp.zip = request.POST['zip']
            #     reg_wp.how_heard = request.POST['how_heard']
            #     reg_wp.comments = request.POST['comments']
            #     reg_wp.phone = request.POST['phone']
            #     reg_wp.business_name = request.POST['business_name']
            #     reg_wp.email = request.POST['email']
            #     reg_wp.save()
            #
            #     print "saved new contract form"
            #     return HttpResponseRedirect("/crm/invoices/interested_detail/"+id+"/")
            #
            # except: raise Http404


        else:
            print "form is not valid"
            # raise Http404

    #deal with change/assign sales
    elif request.is_ajax() and "chooseSales" in request.POST:
        salesID = request.POST.get('chooseSales')
        try:wp = Register_Event.objects.get(id=id)
        except: raise Http404

        try:
            sales = User.objects.get(id=salesID)
            wp.sales = sales
            wp.save()
        except:
            raise Http404

        content = {
            'sales': sales.get_full_name(),
        }
        return JsonResponse(content, safe=False)
    elif "send_aggrement" in request.POST:
        agreement_id = Register_Event_Aggrement.objects.create(register_event=wp)
        agreement_id.code = id_generator(size=25)
        agreement_id.save()
        context = {
            'message':"Click on the following link to view the agrement <br /><br /><a href='https://bayareaweddingfairs.herokuapp.com/crm/view/complete/agreement/%s' target='_blank' class='btn'>Open Agreement</a>"%(agreement_id.code),
            'title':"Bay Area Wedding Fairs Agreement",
            }
        html_content = render_to_string('email/bawf_native_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement", text_content, 'info@bayareaweddingfairs.com', [wp.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        message = "Agreement is sent successfully."

    elif "create_bulk_signal" in request.POST:
        ids = request.POST.getlist('bulk_check')
        print ids
        bulk = BulkInvoices.objects.create(email=wp.email)
        bulk_amount = 0
        for id in ids:
            ine = InvoiceRegisterVendor.objects.get(id=id)
            bulk_amount += ine.deposit
            bulk.invoice_event_vendor.add(ine)
        bulk.amount = bulk_amount
        bulk.save()
        context = {
            'message':"Click on the following link to view the bulk invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/bulk/pay/%s' target='_blank' class='btn'>Open Invoice</a>"%(bulk.id),
            'title':"Bay Area Wedding Fairs Bulk Invoice",
            }
        html_content = render_to_string('email/bawf_email.html', context=context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [wp.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        message = "Invoice request sent successfully."
        print "bulk is created: ",bulk.id
    elif "delete_invoice" in request.POST:

        delete_invoice = request.POST.get('delete_invoice')
        print "delete_invoice: ",delete_invoice
        InvoiceRegisterVendor.objects.get(id=delete_invoice).delete()
        # wp.record_amount_due()
        wp.amount_due = wp.get_amount_due()
        wp.total_amount = wp.get_amount_total()
        wp.have_invoices -= 1
        wp.save()
        return HttpResponseRedirect('')
    elif "delete_contractor" in request.POST:
        wp.status = Register_Event.REMOVED
        wp.amount_due = wp.get_amount_due()
        wp.total_amount = wp.get_amount_total()
        wp.save()
        # wp.record_amount_due()
        return HttpResponseRedirect('/crm/invoices/contracted/')
    elif "assign_sales_person" in request.POST:
        assign_sales_person_2 = request.POST.get('assign_sales_person_2')
        print "sales person assign: ",assign_sales_person_2
        if assign_sales_person_2 != "None":
            wp.sales_id = assign_sales_person_2
            print "Done with sales"
        else:
            wp.sales_id = None
        wp.save()
        return HttpResponseRedirect('')
    # print 'checking edit note id'
    elif "edit_note_id" in request.POST:
        print 'inside edit notes id'
        edit_note_id = request.POST.get('edit_note_id')
        notes_to_edit = Notes.objects.get(id=edit_note_id)
        notes_to_edit.note = request.POST.get('note_text')
        notes_to_edit.save()
        return HttpResponseRedirect('')
    elif "remove_note_id" in request.POST:
        remove_note_id = request.POST.get('remove_note_id')
        note_to_delete = Notes.objects.get(id=remove_note_id).delete()
    elif "edit_invoice" in request.POST:
        edit_invoice = request.POST.get('edit_invoice')
        irv_to_edit = InvoiceRegisterVendor.objects.get(id=edit_invoice)
        if irv_to_edit.payment_method == InvoiceRegisterVendor.CASH:
            irv_to_edit.payment_method = InvoiceRegisterVendor.CHECK
            irv_to_edit.save()
        elif irv_to_edit.payment_method == InvoiceRegisterVendor.CHECK:
            irv_to_edit.payment_method = InvoiceRegisterVendor.CASH
            irv_to_edit.save()
        return HttpResponseRedirect('')
    bulk_invoices = BulkInvoices.objects.filter(email__iexact=wp.email)
    print "bulk invoices: ",bulk_invoices
    #aggrements = Register_Event_Aggrement.objects.filter(register_event=wp)
    invoices = InvoiceRegisterVendor.objects.filter(register=wp)
    staff = User.objects.filter(is_staff=True)
    allow_payment_list = ['Cash', 'Check']
    return render(request, 'vendroid/CRM/interested_contractors_details.html', {
        'allow_payment_list': allow_payment_list,
        'wp': wp,
        'id': id,
        'is_contracted': True,
        'form': noteForm,
        'taskForm': taskForm,
        'notes':notes,
        'staff':staff,
        'tasksComplete':tasksComplete,
        'tasksInProgress':tasksInProgress,
        'error_message': error_message,
        'invoice_form': invoice_form,
        'invoices': invoices,
        'message': message,
        'cont_form': Form,
        # 'aggrements': aggrements,
        'bulk_invoices': bulk_invoices,
    })


@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def bride_detail(request, id):
    pass_id = id
    user = request.user
    error_message = None
    wp = None
    try:
        wp = Register_Event.objects.select_related('event','user','sales').get(id=id)
    except Exception as e:
        print e
        raise Http404
    if request.is_ajax():
        print request.POST
        type = request.POST.get('edit_type')
        value = request.POST.get('edit_value')
        edit_display = request.POST.get('edit_display')
        edit_editor = request.POST.get('edit_editor')
        if type == 'name':
            wp.name = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Name edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'city':
            wp.city = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'City edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'zip':
            wp.zip = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Zip edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'email':


            for ox in Register_Event.objects.filter(email__iexact=wp.email):
                ox.email = value
                ox.save()
            # user_email = wp.user
            # user_email.email = value
            # user_email.username = value
            # user_email.save()
            wp.email = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Email edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'phone':
            wp.phone = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Phone edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'weddingdate':
            wp.weddingDate = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Wedding Date edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'how-heard':
            wp.how_heard = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'How Heard edited successfully.'
                                   })
            return HttpResponse(response)
        elif type == 'comments':
            wp.comments = value
            wp.save()
            response = json.dumps({'edit_editor': edit_editor,
                                   'edit_display': edit_display,
                                   'value': value,
                                   'message': 'Comments edited successfully.'
                                   })
            return HttpResponse(response)

    if "delete_bride" in request.POST:
        wp.status = Register_Event.REMOVED
        wp.save()
        return HttpResponseRedirect(reverse('interested_bg'))

    return render(request, 'vendroid/CRM/interested_brides_details.html', {
        'wp': wp,
        'id': id,
        'is_contracted': True,
        'error_message': error_message,
    })


def send_bawf_email(sendTo, message, title, subject):
    # data = {
    #     'amount' : '10000',
    #     'name' : 'JOHN SMITH',
    #     'address' : '100 MAIN ST PO BOX 1022 SEATTLE WA 98104 USA',
    # }
    context = {
                'message':message,
                'title':title,
                }
    html_content = render_to_string('email/bawf_native_email.html', context=context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, 'Bay Area Wedding Fairs <info@bayareaweddingfairs.com>', [sendTo])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print 'Email sent'




'''
 please convert it to iframe as u will
'''
from yapjoy_registration.models import Company
# @login_required(login_url='/login/')
# @staff_member_required
@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def bg_management_dev(request):
    # user = request.user
    # profile = user.userprofile
    error_message = None
    eventsIDList = None
    cat = ""
    eventsCheck = None
    inteventsIDList = None
    form = bg_registration_form()


    if request.method == "POST":
        form = bg_registration_form(request.POST)
        event_name = ""
        eventsIDList = request.POST.getlist('eventsCheck')
        inteventsIDList = []
        if eventsIDList:
            for x in eventsIDList:
                inteventsIDList.append(int(x))
        else:
            eventsCheck = "Select an event atleast"
        if form.is_valid():
            print 'form is valid'
            data = form.cleaned_data

            print data
            print "eventsIDList: ",eventsIDList
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

                try: weddingDate = data['weddingDate']
                except: weddingDate = ''

                user_reg = None

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
                        cat += "%s "%(c)
                    reg = Register_Event.objects.create(
                                                        user=user_reg,
                                                        name=name,
                                                        phone=phone,
                                                        email=user_reg.email,
                                                        city=city,
                                                        zip=zip,
                                                        comments=comments,
                                                        how_heard=how_heard,
                                                        # categories=cat,
                                                        event=event,
                                                        weddingDate=weddingDate,
                                                        type=Register_Event.BGUSER,
                                                        )
                    event_name += "%s - %s<br />" % (event.name, event.date)

                    for cat in categories:
                        print cat
                        # print cat.id
                        ca = CategoryOptions.objects.get(category=cat)
                        reg.categories.add(ca)





                # message = "Thank you for registering with Bay Area Wedding Fairs.<br /><br /><b>Please print following coupon for each show you have registered or simply show us on smart phone. </b><br /><br /><img height='80%%' width='100%%'  src='https://s3-us-west-2.amazonaws.com/yapjoy-static/static/images/bawf/express_checkin.png' /><br />%s<br /><br />If you like to save time and money, pre-pay online at <a href='http://bayareaweddingfairs.ticketleap.com'>http://bayareaweddingfairs.ticketleap.com</a>. Also, we encourage you to go to our <a href='https://www.facebook.com/baweddingfairs/events'>Facebook Events Page</a>, select the Fair and click on 'Join'. You will be entered in our weekly 'Las Vegas Giveaway' drawing (Winner will be announced on our Facebook page). <br /><br />NEED HELP IN PLANNING? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />if you have any questions, please email us at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com </a><br /><br />We look forward to seeing you at the Wedding Fair<br /><br />Thank You!<br /><br />Bay Area Wedding Fairs" % (
                # event_name)
                # send_bawf_email(sendTo=user_reg.email, message=message, title="",
                #                 subject="Registration Successful!")
                message_information = "First Name: %s<br />Last Name: %s<br />Email: %s<br />Phone: %s<br />City: %s<br />Zip: %s<br />Wedding Fair Interested In: <br />%s<br />Wedding Professional Interested in: %s<br />How do you hear about us: %s<br />Comments: %s<br />"%(firstName, lastName, email, phone, city, zip, event_name, cat, how_heard, comments)
                send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message_information, title="", subject="Bride / Groom Registration Information!")
                return HttpResponseRedirect(reverse('interested_bg'))
            else:

                error_message = "Select an event atleast"
                eventsCheck = "Select an event atleast"
        else:
            error_message = "Form is not valid: ",form.errors


    #coverging events by season
    events = Event_fairs.objects.filter(date__gte=datetime(2017,02,19)).order_by('date')
    content = {
        'form':form,
        'events':events,
        'error_message':error_message,
        'eventsIDList':eventsIDList,
        'inteventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'all_events':events,

    }

    template_name = 'vendroid/CRM/bgReg.html'
    return render(request, 'vendroid/CRM/DevbgReg.html', content)


@csrf_exempt
def bg_management(request):
    # user = request.user
    # profile = user.userprofile
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
            print 'form is valid'
            data = form.cleaned_data

            print data
            print "eventsIDList: ",eventsIDList
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

                try: weddingDate = data['weddingDate']
                except: weddingDate = ''

                user_reg = None

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
                        cat += "%s "%(c)


                    reg = Register_Event.objects.create(
                                                        user=user_reg,
                                                        name=name,
                                                        phone=phone,
                                                        email=user_reg.email,
                                                        city=city,
                                                        zip=zip,
                                                        comments=comments,
                                                        how_heard=how_heard,
                                                        # categories=cat,
                                                        event=event,
                                                        weddingDate=weddingDate,
                                                        type=Register_Event.BGUSER,
                                                        )
                    event_name += "%s - %s<br />" % (event.name, event.date)

                    for cat in categories:
                        print cat
                        # print cat.id
                        try:
                            ca = CategoryOptions.objects.get(category__iexact=cat)
                            reg.categories.add(ca)
                        except:
                            pass





                message = "Thank you for registering with Bay Area Wedding Fairs.<br /><br /><b>Please print following coupon for each show you have registered or simply show us on smart phone. </b><br /><br /><img height='80%%' width='100%%'  src='https://s3-us-west-2.amazonaws.com/yapjoy-static/static/images/bawf/express_checkin.png' /><br />%s<br /><br />If you like to save time and money, pre-pay online at <a href='http://bayareaweddingfairs.ticketleap.com'>http://bayareaweddingfairs.ticketleap.com</a>. Also, we encourage you to go to our <a href='https://www.facebook.com/baweddingfairs/events'>Facebook Events Page</a>, select the Fair and click on 'Join'. You will be entered in our weekly 'Las Vegas Giveaway' drawing (Winner will be announced on our Facebook page). <br /><br />NEED HELP IN PLANNING? Try our new Wedding Planning Platform <a href='https://www.yapjoy.com/'>YAPJOY</a>.<br /><br />if you have any questions, please email us at <a href='mailto:info@bayareaweddingfairs.com'>info@bayareaweddingfairs.com </a><br /><br />We look forward to seeing you at the Wedding Fair<br /><br />Thank You!<br /><br />Bay Area Wedding Fairs" % (
                event_name)
                send_bawf_email(sendTo=user_reg.email, message=message, title="",
                                subject="Registration Successful!")
                message_information = "First Name: %s<br />Last Name: %s<br />Email: %s<br />Phone: %s<br />City: %s<br />Zip: %s<br />Wedding Fair Interested In: <br />%s<br />Wedding Professional Interested in: %s<br />How do you hear about us: %s<br />Comments: %s<br />"%(firstName, lastName, email, phone, city, zip, event_name, cat, how_heard, comments)
                send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message_information, title="", subject="Bride / Groom Registration Information!")
                return HttpResponseRedirect('/crm/invoices/addition/bg/success/iframe/')
            else:

                error_message = "Select an event atleast"
                eventsCheck = "Select an event atleast"
        else:
            error_message = "Form is not valid: ",form.errors


    #coverging events by season
    events = Event_fairs.objects.filter(Q(is_expired=False)&Q(date__gte=datetime.today().date())).order_by('date')
    content = {
        'form':form,
        'events':events,
        'error_message':error_message,
        'eventsIDList':eventsIDList,
        'inteventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'all_events':events,
        'how_heard':how_heard,

    }

    template_name = 'vendroid/CRM/bgReg.html'
    return render(request, 'vendroid/CRM/bgReg.html', content)

conn = boto.connect_s3(
        aws_access_key_id='AKIAIXFGL3W7R47QWV2A',
        aws_secret_access_key='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',
    )
bucket = conn.get_bucket(AWS_STORAGE_BUCKET_NAME)
import sys


def save_to_S3(file_name):

    key_name = file_name
    path = '/static/images/bawf/'
    full_key_name = os.path.join(path, key_name)
    k = bucket.new_key(full_key_name)
    k.set_contents_from_filename(key_name, cb=percent_cb, num_cb=10)
    link_ = 'https://yapjoy-static.s3.amazonaws.com/static/images/bawf/' + file_name

    print "link: ", link_
    os.remove(file_name)
    return link_
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()



@csrf_exempt
def bg_managementv2(request):
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
                try: weddingDate = data['weddingDate']
                except: weddingDate = ''
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
                        cat += "%s "%(c)
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
                message_information = "First Name: %s<br />Last Name: %s<br />Email: %s<br />Phone: %s<br />City: %s<br />Zip: %s<br />Wedding Fair Interested In: <br />%s<br />Wedding Professional Interested in: %s<br />How do you hear about us: %s<br />Comments: %s<br />"%(firstName, lastName, email, phone, city, zip, event_name, cat, how_heard, comments)
                send_bawf_email(sendTo='info@bayareaweddingfairs.com', message=message_information, title="", subject="Bride / Groom Registration Information!")
                return HttpResponseRedirect('/crm/registration/bg/success/iframe/')
            else:
                error_message = "Select an event atleast"
                eventsCheck = "Select an event atleast"
        else:
            error_message = "Form is not valid: ",form.errors
    """
    converging events by season
    """
    events = Event_fairs.objects.filter(Q(is_expired=False)).order_by('date')
    content = {
        'form':form,
        'events':events,
        'error_message':error_message,
        'eventsIDList':eventsIDList,
        'inteventsIDList':inteventsIDList,
        'eventsCheck':eventsCheck,
        'all_events':events,
        'how_heard':how_heard,
    }
    return render(request, 'vendroid/CRM/bgRegV2.html', content)




'''
Please convert to iFrame
'''
from yapjoy_registration.models import Company
# @login_required(login_url='/login/')
# @staff_member_required
@csrf_exempt
def LasVegasReg(request):
    # user = request.user
    error_message = None
    success_message = ""
    form = LasVegasForm()


    if request.method == "POST":
        print "inside post"
        form = LasVegasForm(request.POST)
        if form.is_valid():
            print 'form is valid'
            data = form.cleaned_data
            print data

            firstName = data['firstName']
            lastName = data['lastName']
            email = data['email']
            weddingDate = data['weddingDate']
            name = str(firstName)+' '+str(lastName)

            print email, weddingDate, name
            # try:
            user = None
            try:
                user = User.objects.get(email__iexact=email)
            except:
                user = User.objects.create(email=email, username=email, first_name=firstName, last_name=lastName)
            user_reg = Register_Event.objects.create(event=Event_fairs.objects.filter(date__gte=datetime.now()).order_by('date')[0],
                                          user=user,
                                          name=name,
                                          email=email,
                                          is_lasVegasSignIn=True,
                                          type=Register_Event.BGUSER,
                                          # city=city,
                                          # zip=zip,
                                          # comments=comments,
                                          # how_heard=how_heard,
                                          # category=category,
                                          # event=event,
                                          # business_name=business_name,
                                          # phone=phone,
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
            # except Exception as e:
                # Register_Event.objects.create(  event=Event_fairs.objects.get(name="Las Vegas GiveAway"),
                #                                 user=user,
                #                                 name=name,
                #                                 email=email,
                #                                 is_lasVegasSignIn=True
                #                                 # city=city,
                #                                 # zip=zip,
                #                                 # comments=comments,
                #                                 # how_heard=how_heard,
                #                                 # category=category,
                #                                 # event=event,
                #                                 # business_name=business_name,
                #                                 # phone=phone,
                #                                 )
                # Invoice_Event.objects.create(registered_event=reg, user=user)
                # print 'created las vegas reg'
            # return HttpResponseRedirect('/crm/LasVegasReg/')
        else:
            error_message = "Select an event atleast"

    content = {
        'form':form,
        'success_message':success_message,
    }

    return render(request, 'vendroid/CRM/LasVegasReg.html', content)



@login_required(login_url="/login/")
@staff_member_required
def interested_bg(request):
    # user = request.user
    bgUsers = Register_Event.objects.select_related('event').filter(type=Register_Event.BGUSER).exclude(status=Register_Event.REMOVED).order_by('-created_at')
    # print bgUsers
    if "export_all" in request.POST:
        print 'viewpost'
        output = []
        # event_selected = request.POST.get('csv_export_all', None)
        # csv_export_id = request.POST.get('csv_export_id', None)
        # print 'csv_export_all: ', event_selected, csv_export_id
        response = HttpResponse(content_type='text/CSV')
        response['Content-Disposition'] = 'attachment;filename=export.csv'
        # response.ContentType = "application/CSV";
        # response.AddHeader("Content-Disposition", "attachment;records.csv");
        writer = csv.writer(response)
        search_list = []
        query_set = []
        query_set = bgUsers
        print 'query set: ', query_set
        import unicodedata
        if query_set:
            print 'In query set: ', query_set.count()
            writer.writerow(
                ['Bride/Groom Name', 'Phone', 'Email','City','Zip','Wedding Date','Comments','How heard','Event','Las Vegas Sign In?', 'Created At'])
            for data in query_set:
                name = "N/A"
                if data.name:
                    name = unicodedata.normalize('NFKD', data.name).encode('ascii', 'ignore')
                # business_name = "N/A"
                # if data.business_name:
                #     business_name = unicodedata.normalize('NFKD', data.business_name).encode('ascii', 'ignore')
                email = "N/A"
                if data.email:
                    email = unicodedata.normalize('NFKD', data.email).encode('ascii', 'ignore')
                # name = "N/A"
                # if data.name:
                #     name = unicodedata.normalize('NFKD', data.name).encode('ascii', 'ignore')
                comments = "N/A"
                if data.comments:
                    comments = unicodedata.normalize('NFKD', data.comments).encode('ascii', 'ignore')

                # unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
                # 'first_name','last_name','user__email','amount','frequency','donate_as','phone','occupation','address','city','state','zip'
                output.append([name, data.phone, email,data.city, data.zip, data.weddingDate, comments,data.how_heard,data.event,data.is_lasVegasSignIn, str(data.created_at)])
            writer.writerows(output)
            return response
    # salesCandidates = User.objects.filter(is_superuser=True)
    # print salesCandidates

    return render(request, 'vendroid/CRM/bgViewList.html', {
        'bgUsers': bgUsers,
    })


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_superuser)
def EventList_bg(request):
    bgUsers = None
    tickets = EventTickets()
    events = Event_fairs.objects.all()
    if request.is_ajax():
        event = request.GET.get('event')
        print "event: ", event
        e = events.get(name=event)
        print "events: ", events
        bgUsers = EventTickets.objects.filter(event=e)

        print "filtered: ", bgUsers, bgUsers.query
        html = render_to_string('vendroid/CRM/partial/_grid_search.html', {
            'bgUsers': bgUsers,
            'event': events,
        })
        return HttpResponse(html)
    else:
        bgUsers = EventTickets.objects.all()

    return render(request, 'vendroid/CRM/bgEventList.html', {
        'bgUsers': bgUsers,
        'event': events,
    })


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_superuser)
def promocodelist_bg(request):
    promo = None

    promo = Promocode()
    form = PromoCodeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            print "form valid"
            code = form.cleaned_data.get('code')
            amount = form.cleaned_data.get('amount_percent')
            type = form.cleaned_data.get('type')
            is_Available = form.cleaned_data.get('is_Available')

            print "form: ", code, amount, type, is_Available
            promo.code = code
            promo.amount_percent = amount
            promo.type = type
            promo.is_Available = is_Available
            promo.save()

        else:
            print "form is not valid"
    else:
        print "request is not post"

    promo = Promocode.objects.all()
    return render(request, "vendroid/CRM/bgPromocode.html", {
        'promocode': promo,
        'form': form
    })


def populate_Promocode_bg(request, id):
    promo = Promocode.objects.get(id=id)
    data = {
        'code': promo.code,
        'amount': promo.amount_percent,
        'type': promo.type,
        'is_available': promo.is_Available
    }
    return JsonResponse(data)

@login_required(login_url='/crm/login/')
@csrf_exempt
def edit_Promocode_bg(request):
    if request.method == 'POST':
        print "ajax"
        id = request.POST.get('id')
        code = request.POST.get('code')
        amount = request.POST.get('amount')
        type = request.POST.get('type')
        is_available = request.POST.get('is_available')
        print "id: ", id, code, amount, type, is_available
        promo_update = Promocode.objects.get(id=id)
        print "promo: ", promo_update
        promo_update.code = code
        promo_update.amount_percent = amount
        promo_update.type = type
        if is_available == 'true':
            print "yes"
            promo_update.is_Available = True
        else:
            print "no"
            promo_update.is_Available = False
        promo_update.save()
        data = "success"
        return HttpResponse(data)
    else:
        data = "error"
        return HttpResponse(data)


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_superuser)
# @csrf_exempt
def EventList_bg_CSV(request):
    events = Event_fairs.objects.all()
    filename = None
    if request.method == "POST":
        print "in the post"
        event = request.POST.get('events')
        print "event: ", event
        e = events.get(name=event)
        tickets = EventTickets.objects.filter(event=e)
        output = []
        response = HttpResponse(content_type='text/CSV')
        response['Content-Disposition'] = 'attachment;filename=csv_{}.csv'.format(event).strip()
        print "response: ", response
        writer = csv.writer(response)
        print "writer: ", writer

        writer.writerow(
            ['Event', 'Email', 'Phone', 'Status', 'Quantity', 'Created at'])

        for t in tickets:
            print "t: ", t.event
            output.append([t.event, t.email, t.phone, t.is_attended, t.quantity, t.created_at])
        writer.writerows(output)
        return response

    else:
        print "Not ajax"

        return HttpResponseRedirect('/crm/bridegroom/bg/list')


@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def TasksList(request):

    # sales = SalesTasks()
    # ex = Register_Event.objects.select_related('user')
    # print("query: ", ex.query)
    # vendor = User()

    if request.is_ajax():
        tasks = request.POST.get('task')
        print("tasks: ", tasks)
        if tasks:
            # salesfiltered = SalesTasksEx.objects.filter(Q(status__icontains=tasks)  | Q(sales__username__icontains=tasks) | Q(exhibitor__user__username__icontains=tasks) )
            # print ("events: ", tasks, salesfiltered.query)
            # print salesfiltered.query
            salesfiltered = SalesTasksEx.objects.filter(
                # Q(status__icontains=tasks)  |
                                                        Q(sales_id=tasks)
                                                        # | Q(exhibitor__user__username__icontains=tasks) | Q(exhibitor__user__first_name__icontains=tasks)|  Q(exhibitor__user__last_name__icontains=tasks)
                                                        )
            # print ("events: ", tasks, salesfiltered.query)
            html = render_to_string('vendroid/CRM/partial/_sales_search.html', {
                'tasks': salesfiltered
            })
            return HttpResponse(html)
    # else:
    #     sales = SalesTasksEx.objects.all()
        # print ("sales: ", sales)
    sales = SalesTasksEx.objects.all().distinct('sales').values('sales_id')
    users = User.objects.filter(id__in=sales)

    return render(request, 'vendroid/CRM/tasks_list.html', {
        # 'tasks': sales,
        'sales':users
    })

@login_required(login_url='/crm/login/')
def search(request):
    if request.is_ajax():
        search = request.GET.get('search', None)
        type = request.GET.get('type', None)
        search = search.split(' ')[0]
        events = None
        if type == 'name':
            print ("name")
            events = Register_Event_Interested.objects.filter(user__username__icontains=search)
        elif type == 'email':
            print ("email")
            events = Register_Event_Interested.objects.filter(user__email__icontains=search)
        elif type == 'phone':
            print ("phone")
            events = Register_Event_Interested.objects.filter(phone__icontains=search)
        elif type == 'category':
            print ("phone")
            events = Register_Event_Interested.objects.filter(category__icontains=search)
        elif type == 'created_date':
            print ("created date")
            events = Register_Event_Interested.objects.filter(create_at__icontains=datetime.strptime(search, '%Y-%m-%d').date())
        elif type == 'business':
            print ("busin")
            events = Register_Event_Interested.objects.filter(business_name__icontains=search)
        else:
            print ('all')
            events = Register_Event_Interested.objects.all()
        # events = Register_Event_Interested.objects.filter(Q(user__username__icontains=search)|Q(user__email__icontains=search)|Q(business_name__icontains=search)|
        #                                                   Q(phone__icontains=search)|Q(name__icontains=search)).order_by('-created_at')
        print ('search: ', search)
        print ('event: ', events, events.count())

        string = render_to_string('vendroid/CRM/partial/_search_interested_vendors.html', {

            'event':events
        })
        return HttpResponse(string)

    else:
        print ('not ajax')

    return render(request, 'vendroid/CRM/search.html')

@login_required(login_url='/crm/login/')
def search_contracted(request):
    if request.is_ajax():
        search = request.GET.get('search', None)
        search = search.split(' ')[0]
        initial_word = search
        search = search.split(' ')[0]
        # wps = Register_Event.objects.select_related('event').exclude(type=Register_Event.BGUSER).filter(
        #     email__icontains=search).exclude(status=Register_Event.REMOVED).order_by('-created_at')
        wps =  Register_Event.objects.filter(Q(event__name__icontains=search)|Q(user__username__icontains=search)
                                                  |Q(user__email__icontains=search)|Q(business_name__icontains=search)|Q()).exclude(status=Register_Event.BGUSER).order_by('-created_at')


        print ('search: ', search)
        print ('wps: ', wps)
        eventdata = ''
        events = ''
        string = render_to_string('vendroid/CRM/partial/_search_interested_vendors.html',{
            'bridegrooms': eventdata,
            'contracted': wps,
            'event':events

        })
        return HttpResponse(string)

    else:
        return HttpResponse('')

@login_required(login_url='/crm/login/')
def search_bridegrooms(request):
    if request.is_ajax():
        search = request.GET.get('search', None)
        search = search.split(' ')[0]
        initial_word = search
        search = search.split(' ')[0]
        # eventdata = Register_Event.objects.select_related('event', 'sales').filter(
        #     event__name__icontains=search).order_by('-created_at')
        eventdata = Register_Event.objects.filter(Q(event__name__icontains=search)|Q(user__username__icontains=search)
                                                  |Q(user__email__icontains=search)|Q(business_name__icontains=search)|Q()).exclude(status=Register_Event.BGUSER).order_by('-created_at')
        wps = ''
        events = ''
        print ('search: ', search)
        print ('eventdata: ', eventdata)
        string = render_to_string('vendroid/CRM/partial/_search_interested_vendors.html', {
            'bridegrooms': eventdata,
            'contracted': wps,
            'event':events
        })
        return HttpResponse(string)


def check_string(t):
    if t:
        printable = set(string.printable)
        return filter(lambda x: x in printable, t)

@login_required(login_url='/crm/login/')
@csrf_exempt
def csv_generate(request):

    if request.method == 'POST':
        search = request.POST.get('hidden_search', None)
        type = request.POST.get('hidden_type', None)
        search = search.split(' ')[0]
        print ("search: ", search, request.POST.get('hidden_type', None))
        events = None
        if type == 'name':
            print ("name")
            events = Register_Event_Interested.objects.filter(user__username__icontains=search)
            print (events.count())
        elif type == 'email':
            print ("email")
            events = Register_Event_Interested.objects.filter(user__email__icontains=search)
        elif type == 'phone':
            print ("phone")
            events = Register_Event_Interested.objects.filter(phone__icontains=search)
        elif type == 'category':
            print ("phone")
            events = Register_Event_Interested.objects.filter(category__icontains=search)
        elif type == 'created_date':
            print ("created date")
            events = Register_Event_Interested.objects.filter(created_at=datetime.strptime(search, '%Y-%M-%D'))
        elif type == 'business':
            print ("busin")
            events = Register_Event_Interested.objects.filter(business_name__icontains=search)
        else:
            print ('all')
            events = Register_Event_Interested.objects.all()

        output = []
        response = HttpResponse(content_type='text/CSV')
        response['Content-Disposition'] = 'attachment;filename=csv_{}.csv'.format('asd').strip()

        writer = csv.writer(response)
        print ("writer: ", writer, events.count(), events)

        writer.writerow(
            ['Vendor Name', 'Email', 'Phone', 'Company', 'Business Category', 'Created at'])

        for t in events:
            output.append([check_string(t.user.username), check_string(t.user.email), check_string(t.phone), check_string(t.business_name), check_string(t.category), (t.created_at.date())])
        writer.writerows(output)
        return response

    # return render(request, 'vendroid/CRM/search.html')


@csrf_exempt
def ticketingPrice(request):
    event_fairs = Event_fairs.objects.all().order_by('-date')
    ticket = EventTicketForm()

    if request.method == 'POST':
        print ("post")
        name = request.POST.get('name')
        standard_amount = request.POST.get('standard_amount')
        early_bird_amount = request.POST.get('early_bird_amount')
        group_amount = request.POST.get('group_amount')
        event_date = request.POST.get('event_date')
        is_Expire = request.POST.get('is_Expire')
        event_id = request.POST.get('event_id')

        print ("form: ", event_date,is_Expire, name, standard_amount, early_bird_amount, group_amount, event_id)
        event = event_fairs.get(id=event_id)
        event.name = name
        if standard_amount:
            event.amount = standard_amount
        if early_bird_amount:
            event.earlybird_ticket = early_bird_amount
        if group_amount:
            event.group_ticket = group_amount
        if is_Expire:
            event.is_expired = True
        else:
            event.is_expired = False
        event.date = datetime.strptime(event_date, "%Y-%M-%d").date()
        event.save()


    else:
        print ("request is not post")


    context = {
        'events': event_fairs,
        'form':ticket
    }
    return render(request, 'vendroid/CRM/ticketPrice.html', context)

@login_required(login_url='/crm/login/')
def eventdata(request):
    event_data = None
    if request.is_ajax():
        event = request.GET.get("event")
        event_data = Event_fairs.objects.get(id=event)
    data = {
        'name':event_data.name,
        'standard':event_data.amount,
        'early_birds':event_data.earlybird_ticket,
        'group':event_data.group_ticket,
        'expire': event_data.is_expired,
        'date' : str(event_data.date)
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required(login_url='/crm/login/')
def ticket_search(request):
    string = ''
    if request.is_ajax():
        ticket = request.GET.get('ticket')
        print ("ticket ")
        if ticket:
            event_fair = Event_fairs.objects.filter(name__icontains=ticket)
            print (event_fair)
            string = render_to_string('vendroid/CRM/partial/_grid_ticketing_price.html', {
                'events':event_fair
            })
            return HttpResponse(string)
    else:
        return HttpResponse('')

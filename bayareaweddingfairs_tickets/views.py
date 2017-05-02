from django.shortcuts import render
from yapjoy_files.models import Event_fairs
from django.http import HttpResponse
from datetime import datetime
from .forms import *
from bayareaweddingfairs_tickets.models import *#EventTickets, Promocode, id_generator
import stripe
from django.http import JsonResponse


def Main(request):
    events = Event_fairs.objects.filter(date__gte=datetime.now())
    return render(request, 'vendroid/bayareaweddingfairs_tickets/main.html',{
        'events':events,
    })


promocode_code = ''
total = ''
discount = ''
token = ''
quantity = ''


def PromoCode_Validate(request):
    if request.is_ajax():
        print "ajax confirmed"
        global promocode_code, total, discount, quantity
        promocode_code = request.GET.get('promocode')
        total = request.GET.get('total_text')
        quantity = request.GET.get('quantity')
        eventID = request.GET.get('eventid')
        earlyQuantity = request.GET.get('earlyquantity')
        quantityTickets = request.GET.get('quantityTickets')
        groupquantity = request.GET.get('groupquantity')
        total = float(total)
        print promocode_code, total, discount, quantity, eventID, earlyQuantity, quantityTickets, groupquantity
        event = Event_fairs.objects.get(id=eventID)
        print "evevnt: ", event.earlybird_ticket, event.group_ticket
        try:
            validcode = Promocode.objects.get(code=promocode_code)
            v = validcode
            if v.is_Available:
                amount = v.amount_percent
                type = v.type
                if (v.type == 'amount') & (total != ''):
                    earlyPrice = float(event.earlybird_ticket) - float(amount)
                    ticketPrice = float(event.amount) - float(amount)
                    groupPrice = float(event.group_ticket)
                    total = earlyPrice * int(earlyQuantity) + ticketPrice * int(quantityTickets) + groupPrice * int(groupquantity)
                    discount = total

                elif (v.type == 'percent') & (total != ''):

                    earlyPrice = (float(event.earlybird_ticket)/100)* float(amount)
                    ticketPrice = (float(event.amount)/100)* float(amount)
                    groupPrice = float(event.group_ticket)
                    total = earlyPrice * int(earlyQuantity) + ticketPrice * int(quantityTickets) + groupPrice * int(
                        groupquantity)
                    discount = total
                print "final discount:", discount
                data = {'response': 'success', 'discount': discount}
                return JsonResponse(data)
            else:
                data = {'response': 'error', 'error': 'Offer is not valid'}
                return JsonResponse(data)

        except Exception as e:
            data = {'response': 'error', 'error': 'query no exist'}
            print "this is exception ", e
            return JsonResponse(data)
    else:
        print "not ajax"
        data = {'response': 'error', 'error': 'error in ajax'}
        return JsonResponse(data)

from yapjoy import settings
def BuyTickets(request, id):
    # secret_key = 'sk_test_enH3Di38sTWreGlOZPBNML93'
    # pub_key = 'pk_test_tZdpLY6bm1aDvhy9tBdfyMeV'
    stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
    global promocode_code
    event = Event_fairs.objects.get(id=id)
    ticketform = CreditCardTicketForm(initial={
        # 'email':'adeelpkpk@gmail.com',
        'number':'4242424242424242',
        'year':'2017',
        'phone':'2017'
    })
    print "in the but ticket"
    valid_code = ""
    error_message = ""
    amount = 0
    promo_code_discount = None
    if request.method == 'POST':
        ticketform = CreditCardTicketForm(request.POST or None)
        if ticketform.is_valid():
            print 'form'
            email = ticketform.cleaned_data.get('email')
            # number = ticketform.cleaned_data.get('number')
            phone = ticketform.cleaned_data.get('phone')
            month = ticketform.cleaned_data.get('month')
            year = ticketform.cleaned_data.get('year')
            stripe_token = request.POST.get('stripe_token')
            promocode = request.POST.get('promocode')
            quantity_tickets = request.POST.get('quantityTickets')
            print quantity_tickets
            amount = float(event.amount) * float(int(quantity_tickets))
            try:
                promo_code_discount = Promocode.objects.get(code=promocode)
                if promo_code_discount.is_Available:
                    if promo_code_discount.type == Promocode.AMOUNT:
                        amount -= float(promo_code_discount.amount_percent)
                    elif promo_code_discount.type == Promocode.PERCENT:
                        amount = (amount / 100)*float(Promocode.amount_percent)
            except Exception as e:
                print e
            amount = int(amount*100)
            print "Amount in cents: ",amount
            charge = None
            if stripe_token:
                charge = stripe.Charge.create(
                    amount=amount,  # amount in cents, again
                    currency="usd",
                    source=stripe_token,
                    description="Ticket purchased by %s, quatity: %s, amount: %s"%(email, quantity_tickets, amount)
                )
                print charge
            print "data: ", phone, month, year,quantity_tickets, stripe_token, email, event, total, promocode_code, amount

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
                    result = send_email_bawf(sender="info@bayareaweddingfairs.com", subject="Ticket Reservation ",
                                            receive=email,
                                            message='Thank you for reservation '+ str(event.name )+ "Your Code is: \n" +code)
                    # if result == True:
                    return render(request, "vendroid/bayareaweddingfairs_tickets/thankyou_page.html",)
            except Exception as e:
                print "exceptionBuyTickets: ", e.message

        else:
            print "form not valid"
    context = {
        'pub_key': settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'event':event,
        'form':ticketform
    }

    return render(request, 'vendroid/bayareaweddingfairs_tickets/buy_tickets.html',context)


def checkout_ajax(request):
    print "checkout", request

    # secret_key = 'sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt'
    # pub_key = 'pk_test_ic11SWVPcUHwZ1mDBEBTdSX1'
    token = None

    pub_key = 'pk_test_ic11SWVPcUHwZ1mDBEBTdSX1'#settings.STRIPE_PUBLISHABLE_KEY_BAWF
    secret_key = 'sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt'#settings.STRIPE_SECRET_KEY_BAWF

    if request.is_ajax():
        print "ajax confirmed"
        amount = request.GET.get('amount')
        card = request.GET.get('card')
        expM = request.GET.get('expM')
        expY = request.GET.get('expY')

        print amount, card, expM, expM
        # stripe.api_key = "sk_test_z3b8Yfc0Mcuh0P3M7VDfGZkt"
        stripe.api_key = secret_key
        #user, created = UserStripe.objects.get_or_create(user=request.user)
        #print user
        token = stripe.Token.create(
            card={
                "number": card,
                "exp_month": expM,
                "exp_year": expY,

            },
        )
        print "token:", token

        if token:
            print "token created "
            try:

                charge = stripe.Charge.create(
                    amount=amount, # amount in cents, again
                    currency="usd",
                    source=token,
                    description="Example charge"
                )
                print "charge", charge

                if charge:
                    return HttpResponse("Success")
                else:
                    print "error in charge"
                    return HttpResponse("Fail")

            except stripe.error.CardError as e:
                # The card has been declined
                print "try error: ", e
                return HttpResponse("Fail")

        else:
            print "error in token"
            return HttpResponse("Fail")

        #return HttpResponse("Success")

    else:
        print "error in ajax request"
        return HttpResponse("Fail")


from smtplib import SMTP_SSL

from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string

# s = SMTP_SSL('smtp.gmail.com', 465, timeout=10)
# s.set_debuglevel(1)


def send_email_bawf(sender,subject, receive,message ,title=None):
    top_content = None

    try:

        context_email = {
                'heading' : subject,
                'sub_heading' : top_content,
                'message':message,
                'title':subject,
                'name':receive
            }
        print 'recieve: ', receive
        html_content = render_to_string('email/ticket_reservation.html', context_email)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, sender, [str(receive)], bcc=['adeel@yapjoy.com','info@bayareaweddingfairs.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print "email sent: ",receive
        return True

    except Exception as e:
        print "e: ", e
        print "email not sent"

        return False


def send_email_ticket_bawf(sender,subject, receive,message,link ,title=None, object=None):
    top_content = None

    try:

        context_email = {
                'heading' : subject,
                'sub_heading' : top_content,
                'message':message,
                'title':subject,
                'name':receive,
                'object':object,
                'link':link
            }
        print 'recieve: ', receive
        html_content = render_to_string('email/bawf_native_ticket_email.html', context_email)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, sender, [str(receive)], bcc=['adeel@yapjoy.com','info@bayareaweddingfairs.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print "email sent: ",receive
        return True

    except Exception as e:
        print "e: ", e
        print "email not sent"

        return False

def send_email_ticket_bawf_ticket(sender,subject, receive,message):
    top_content = None

    try:

        context_email = {
                'heading' : subject,
                'sub_heading' : top_content,
                'message':message,
                'title':subject,
                'name':receive,
            }
        print 'recieve: ', receive
        html_content = render_to_string('email/ticket_summary.html', context_email)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, sender, receive)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print "email sent: ",receive
        return True

    except Exception as e:
        print "e: ", e
        print "email not sent"

        return False

from django.shortcuts import render, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import stripe
from yapjoy import settings
from billing import CreditCard, get_gateway
from .forms import CreditCardDepositConfirmForm, CreditCardDepositConfirmFormCoin
from .models import CreditPackages, Transaction, TransactionHistory

@login_required(login_url='/login/')
def credit(request):
    credits = CreditPackages.objects.filter(status=CreditPackages.SHOW)
    context = {
        'credits':credits,
    }
    return render(request, 'iFrame/credit.html', context)



@login_required(login_url='/login/')
def creditBuy(request, id):
    credit = None
    credits = None
    try:
        credit = CreditPackages.objects.get(id=id)
        credits = CreditPackages.objects.all().exclude(id=id)
    except:
        raise Http404
    # initial = {}
    customer_failed = False
    is_customer = None
    amount = None
    stripeError = ""
    user = request.user
    userprofile = user.userprofile
    successMessage = None
    initial = {
        'name':'A k',
        'number':'4242424242424242',
        'verification_value':'112',
        'month':'01',
        'year':'2017',
        'amount':'10',
    }
    try:
        if userprofile.stripe_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
            print 'is customer: ',is_customer_data.sources['data'][0]['last4']
            is_customer = is_customer_data.sources['data'][0]['last4']
    except:
        customer_failed = True
    form = CreditCardDepositConfirmForm(initial=initial)
    if request.method == "POST":
        if "cc_form_submit" in request.POST:
            form = CreditCardDepositConfirmForm(request.POST)
            if form.is_valid():
                try:
                    print 'valid'
                    data = form.cleaned_data
                    amount_coins = credit.amount
                    name = data['name']
                    number = data['number']
                    month = data['month']
                    year = data['year']
                    verification_value = data['verification_value']
                    merchant = get_gateway("modified_stripe")
                    stripe_token = request.POST.get("stripe_token")
                    print 'stripe token: ', stripe_token
                    print 'inside CC'
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    stripe_customer = stripe.Customer.create(
                        email=user.email,
                        card=request.POST.get("stripe_token")
                    )
                    print 'customer: ',stripe_customer

                    if stripe_customer:
                        userprofile.stripe_id = stripe_customer.id
                    userprofile.save()
                    print 'about to response'
                    response = stripe.Charge.create(
                    amount=int(100) * int(str(amount_coins)),  # Convert dollars into cents
                    currency="usd",
                    customer=userprofile.stripe_id,
                    description=user.email,
                    )

                    try:
                        if userprofile.stripe_id:
                            stripe.api_key = settings.STRIPE_SECRET_KEY
                            is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
                            print 'is customer: ',is_customer_data.sources['data'][0]['last4']
                            is_customer = is_customer_data.sources['data'][0]['last4']
                    except:
                        pass
                    print response
                    if response:  # handle invalid response
                        print 'PAYMENT DONE'
                        userprofile.amount+=credit.credits
                        Transaction.objects.create(user=user, amount =str(amount_coins), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                        TransactionHistory.objects.create(user=user, event="Credit deposited to the account.", amount=int(str(amount_coins)))
                        userprofile.save()
                        successMessage = "Credit has been added successfully."
                        # send_donation_email(tplVar, user.email)
                        # return HttpResponseRedirect('/account/')
                except Exception as e:
                    print 'here error:', e
                    stripeError = "Your card was declined."
        elif "cc_form_submit_cus" in request.POST:
            amount = credit.amount
            if not amount == "" or amount == "None":
                try:
                    amountCheck = int(str(amount))
                    if amountCheck == None or amountCheck == 0:
                        pass
                    else:
                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        response = stripe.Charge.create(
                        amount=int(100) * int(str(amount)),  # Convert dollars into cents
                        currency="usd",
                        customer=userprofile.stripe_id,
                        description=user.email,
                        )
                        print response
                        if response:  # handle invalid response
                            print 'PAYMENT DONE'
                            Transaction.objects.create(user=user, amount =str(amount), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                            TransactionHistory.objects.create(user=user, event="Credit deposited to the account.", amount=int(str(amount)))

                            userprofile.amount+=credit.credits
                            userprofile.save()
                            successMessage = "Credit has been added successfully."
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
    }
    return render(request,'iFrame/account.html', content)\

from datetime import datetime
@login_required(login_url='/login/')
def creditBuyiFrame(request):
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
    initial = {
        # 'name':'A k',
        # 'number':'4242424242424242',
        # 'verification_value':'112',
        # 'month':'01',
        # 'year':'2017',
        # 'amount':'10',
    }
    try:
        if userprofile.stripe_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
            print 'is customer: ',is_customer_data.sources['data'][0]['last4']
            is_customer = is_customer_data.sources['data'][0]['last4']
    except:
        customer_failed = True
    form = CreditCardDepositConfirmForm()
    if request.method == "POST":
        if "cc_form_submit" in request.POST:
            form = CreditCardDepositConfirmForm(request.POST)
            if form.is_valid():
                try:
                    print 'valid'
                    data = form.cleaned_data
                    amount_coins = 30
                    # name = data['name']
                    number = data['number']
                    month = data['month']
                    year = data['year']
                    # verification_value = data['verification_value']
                    merchant = get_gateway("modified_stripe")
                    stripe_token = request.POST.get("stripe_token")
                    print 'stripe token: ', stripe_token
                    print 'inside CC'
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    stripe_customer = stripe.Customer.create(
                        email=user.email,
                        card=request.POST.get("stripe_token")
                    )
                    print 'customer: ',stripe_customer

                    if stripe_customer:
                        userprofile.stripe_id = stripe_customer.id
                    userprofile.save()
                    print 'about to response'
                    response = stripe.Charge.create(
                    amount=int(100) * int(str(amount_coins)),  # Convert dollars into cents
                    currency="usd",
                    customer=userprofile.stripe_id,
                    description=user.email,
                    )

                    try:
                        if userprofile.stripe_id:
                            stripe.api_key = settings.STRIPE_SECRET_KEY
                            is_customer_data = stripe.Customer.retrieve(userprofile.stripe_id)#.cards.all(limit=1)['data'][0]['last4']
                            print 'is customer: ',is_customer_data.sources['data'][0]['last4']
                            is_customer = is_customer_data.sources['data'][0]['last4']
                    except:
                        pass
                    print response
                    if response:  # handle invalid response
                        print 'PAYMENT DONE'
                        userprofile.subscribed=True
                        Transaction.objects.create(user=user, amount =str(amount_coins), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                        TransactionHistory.objects.create(user=user, event="Credit deposited to the account.", amount=int(str(amount_coins)))
                        userprofile.amount += 100
                        userprofile.save()
                        reload_window = 'Reload'
                        try:
                            from yapjoy_registration.models import SubscribedUsers
                            su = SubscribedUsers.objects.get(user=user)
                            su.no_of_months = 1
                            su.subscription_date = datetime.now()
                            su.amount = 30
                            su.save()
                            # su.subscription_date = datetime.now()
                        except:
                            SubscribedUsers.objects.create(user=user, no_of_months=1, amount=30)
                        successMessage = "$30 Subscription has been successfully activated."
                        # send_donation_email(tplVar, user.email)
                        # return HttpResponseRedirect('/account/')
                except Exception as e:
                    print 'here error:', e
                    stripeError = "Your card was declined."
        elif "cc_form_submit_cus" in request.POST:
            amount = 30
            if not amount == "" or amount == "None":
                try:
                    amountCheck = int(str(30))
                    if amountCheck == None or amountCheck == 0:
                        pass
                    else:
                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        response = stripe.Charge.create(
                        amount=int(100) * amount,  # Convert dollars into cents
                        currency="usd",
                        customer=userprofile.stripe_id,
                        description=user.email,
                        )
                        print response
                        if response:  # handle invalid response
                            print 'PAYMENT DONE'
                            Transaction.objects.create(user=user, amount = str(30), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                            TransactionHistory.objects.create(user=user, event="Subscription Purchased.", amount=int(str(amount)))

                            userprofile.subscribed=True
                            userprofile.amount += 100
                            userprofile.save()
                            successMessage = "$10 Subscription has been successfully activated."
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
        'key':settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request,'iFrame/subscription_iFrame.html', content)

@login_required(login_url='/login/')
def creditBuyiFrameCoin(request):
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
                    pledge = data['package']
                    # verification_value = data['verification_value']
                    merchant = get_gateway("modified_stripe")
                    stripe_token = request.POST.get("stripe_token")
                    print 'stripe token: ', stripe_token
                    print 'inside CC'
                    stripe.api_key = settings.STRIPE_SECRET_KEY
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
                        amount=int(100) * (pledge.amount),  # Convert dollars into cents
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
                        Transaction.objects.create(user=user, amount =str(amount_coins), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                        TransactionHistory.objects.create(user=user, event="Credit purchased to the account.", amount=int(str(amount_coins)))
                        userprofile.amount += pledge.credits
                        userprofile.save()
                        reload_window = 'Reload'
                        # try:
                        #     from yapjoy_registration.models import SubscribedUsers
                        #     SubscribedUsers.objects.create(user=user, no_of_months=1, amount=10)
                        # except:
                        #     pass
                        successMessage = "%s coins are added successfully."%(pledge.credits)
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
                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        response = stripe.Charge.create(
                        amount=int(100) * amount,  # Convert dollars into cents
                        currency="usd",
                        customer=userprofile.stripe_id,
                        description=user.email,
                        )
                        print response
                        if response:  # handle invalid response
                            print 'PAYMENT DONE'
                            Transaction.objects.create(user=user, amount = str(10), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                            TransactionHistory.objects.create(user=user, event="Subscription Purchased.", amount=int(str(amount)))

                            userprofile.subscribed=True
                            userprofile.amount += 10
                            userprofile.save()
                            successMessage = "$10 Subscription has been successfully activated."
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
    }
    return render(request,'iFrame/subscribe_iFrame_Coin.html', content)

@login_required(login_url='/login/')
def removeCard(request):
    user = request.user
    userprofile = user.userprofile
    userprofile.stripe_id = ''
    userprofile.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
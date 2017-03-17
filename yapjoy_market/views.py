from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import *
from yapjoy_registration.models import *
import json
from django.db.models import Q
import string
import random
from yapjoy_server.views import send_news
from django.db.models import Sum
from django.http import JsonResponse


def growthGraph(request):
    product = None
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.PROFESSIONAL:
        product=Product.objects.filter(awarded_to__user=user).order_by('-amount')
    else:
        product=Product.objects.filter(user=user).order_by('-amount')
    res=[]
    amount = 0
    for obj in product:
        try:
            amount += obj.amount
        except:
            pass
        res.append(
            [str(obj.title),obj.amount]
        )
    if amount == 0:
        res.append(
            ["No plans available",1]
        )
    data = json.dumps(res)
    return HttpResponse(data, content_type='application/json')


@login_required(login_url='/login/')
def myPlanner(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.PROFESSIONAL or profile.type == UserProfile.OTHER:
        raise Http404
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title = data['title']
            description = data['description']
            amount = data['amount']
            category = data['category']
            end_date = data['end_date']
            try:
                amount = int(amount)
            except:
                amount = 0
            pr = Product.objects.create(user=user, title=title, description=description, amount=amount, end_date=end_date, status=Product.PENDING)
            if category:
                pr.category = category
                pr.save()
            send_news('<b>%s</b> added a new plan <b>%s</b>.'%(user.get_full_name(), title))
            return HttpResponseRedirect('/plans/%s'%(pr.id))
    products = Product.objects.filter(user=user).select_related('user').order_by('created_at')
    context = {
        'products':products,
        'form':form,
        'profile':profile,
    }
    return render(request, 'vendroid/market/market.html', context)

@login_required(login_url='/login/')
def market(request):
    user = request.user
    profile = user.userprofile
    # form = ProductForm()
    # if request.method == 'POST':
    #     form = ProductForm(request.POST)
    #     if form.is_valid():
    #         data = form.cleaned_data
    #         title = data['title']
    #         description = data['description']
    #         amount = data['amount']
    #         end_date = data['end_date']
    #         try:
    #             amount = int(amount)
    #         except:
    #             amount = 0
    #         Product.objects.create(user=user, title=title, description=description, amount=amount, end_date=end_date)
    products = None
    if "categories" in request.GET:
        options = optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search_id',flat=True)
        products = Product.objects.filter(is_completed=False,status="Active",category__in=options).select_related('user').order_by('created_at')
    else:
        products = Product.objects.filter(is_completed=False,status="Active").select_related('user').order_by('created_at')

    print "counts", len(products)

    context = {
        'products':products,
        # 'form':form,
    }
    return render(request, 'vendroid/market/professional/market.html', context)

from yapjoy_registration.models import Notifications
@login_required(login_url='/login/')
@csrf_exempt
def plans_detail(request, id):
    user = request.user
    product = None
    profile = user.userprofile
    try:
        product = Product.objects.select_related('user').get(id=id, user=user)
    except:
        raise Http404
    pledges = Pledge.objects.filter(product=product).order_by('amount')
    message = None
    message_failed = None
    if 'delete_plan' in request.POST:
        try:
            if product.amount_min < 1:
                Product.objects.select_related('user').get(id=id, user=user).delete()
                return HttpResponseRedirect('/plans/')
            else:
                print 'Inside else message'
                message_failed = "You can only delete a plan without any bids on it."
        except:
            raise Http404
    if request.is_ajax():
        id = request.POST.get('id')
        if request.user == product.user:
            pledge_award = Pledge.objects.get(id=id)
            pledge_award.is_awarded = True
            pledge_award.save()
            product.awarded_to = pledge_award
            product.is_completed = True
            product.save()
            send_news('%s bid is awarded for the plan %s.'%(product.title, pledge_award.user.get_full_name()))
            Notifications.objects.create(userprofile=pledge_award.user.userprofile, message="You have been awarded a plan by %s"%(request.user.get_full_name()))
            send_email(pledge_award.user.email, message="You have been awarded a plan by %s"%(request.user.get_full_name()), title="Your bid has been accepted.", subject="Congratulations. your bid has been accepted on YapJoy")
            return HttpResponse('success')
        else:
            return HttpResponse('successFalse')
    form = None

    if product.amount_min < 1:
        initial = {
            'title':product.title,
            'description':product.description,
            'category':product.category,
            'amount':product.amount,
            'end_date':product.end_date,
        }
        form = ProductForm(initial=initial)
        if request.method == 'POST' and "editPlan" in request.POST:
            form = ProductForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                title = data['title']
                description = data['description']
                amount = data['amount']
                category = data['category']
                end_date = data['end_date']
                product.title = title
                product.description = description
                product.amount = amount
                product.category = category
                product.end_date = end_date
                product.save()
                message = "Plan is edited successfully."
            else:
                print "Form is invalid"
    if 'publish' in request.POST:
        print ' i m published'
        product.status=Product.ACTIVE
        product.save()
        message = "Your plan is published"
    context = {
        'product':product,
        'pledges':pledges,
        'profile':profile,
        'form':form,
        'message':message,
        'message_failed':message_failed,
        'message_failed':message_failed,
    }
    return render(request, 'vendroid/market/market_detail.html', context)\

from yapjoy_registration.views import send_email
@login_required(login_url='/login/')
@csrf_exempt
def market_detail(request, id):
    error = None
    user = request.user
    form = PledgeForm()
    profile = user.userprofile
    product = Product.objects.select_related('user').get(id=id)
    pledges = Pledge.objects.filter(product=product).order_by('amount')
    current_bid = None
    try:
        current_bid = Pledge.objects.get(user=user, product=product)
    except:
        pass
    if request.POST:
        form = PledgeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not product.is_completed:
                message = data['message']
                amount = data['amount']
                plan = Pledge.objects.create(user=user, product=product, amount=amount, message=message)
                send_news('<b>%s</b> placed a bid on the plan <b>%s</b>.'%(user.get_full_name(), product.title))
                Notifications.objects.create(userprofile=product.user.userprofile, message="%s placed a bid on your plan %s"%(request.user.get_full_name(), product.title))
                send_email(product.user.email, message="A new bid is placed by %s on your plan."%(request.user.get_full_name()), title="New bid received", subject="%s placed a bid on your plan %s"%(request.user.get_full_name(), product.title))
            else:
                error = "This product is awarded already."
    context = {
        'product':product,
        'pledges':pledges,
        'profile':profile,
        'form':form,
        'error':error,
        'current_bid':current_bid,
    }
    return render(request, 'vendroid/market/professional/market_detail.html', context)


@login_required(login_url='/login/')
def rsvp(request):
    print 'here'
    user = request.user
    full_name=user.first_name + user.last_name
    profile = user.userprofile
    email_exists = None
    success_message = None

    if profile.type == UserProfile.PROFESSIONAL or profile.type == UserProfile.OTHER:
        raise Http404
    all_friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile')
    rsvpUserSent = RsvpSend.objects.filter(user=user).values_list('invited_user',flat=True)
    rsvpAccepted = RsvpSend.objects.filter(user=user,status='Accepted').values_list('invited_user',flat=True)
    rsvpEmails = RsvpToEmails.objects.filter(user=user)
    if "invite_id" in request.POST and request.method == "POST":
        print 'here'
        id = request.POST.get('invite_id')
        id = int(str(id))
        user = request.user
        print user.email
        profile = user.userprofile
        if profile.type == UserProfile.PROFESSIONAL or profile.type == UserProfile.OTHER:
            raise Http404

        print 'in try'
        invited_user = User.objects.get(id=id)
        code = id_generator()
        print 'code',code

        print 'sent  email',invited_user.email
        rsvpCount = None
        rsvpCountCreated = None
        rsvpSent = None
        try:
            rsvpCount=RsvpCount.objects.get(user=user)
        except:
            rsvpCount=RsvpCount.objects.create(user=user,rsvp_count=1)
            rsvpCountCreated = True

        try:
            rsvpSent = RsvpSend.objects.get(user=user,invited_user=invited_user,status='Pending')
            success_message = "Your invitation has been sent again."
        except:
            rsvpSent = RsvpSend.objects.create(user=user,invited_user=invited_user,code=code,status='Pending')
            success_message = "Your invitation has been sent."
            if not rsvpCountCreated:
                rsvpCount.rsvp_count += 1
                rsvpCount.save()
        send_email(invited_user.email, message="You have been invited by %s.<br/><br/>If you want to accept invitation,then kindly click link below.<br /><br /><a target='_blank' href='https://www.yapjoy.com/invitationaccepted/%s/%s/%s'>ACCEPT INVITATION</a>"%(request.user.get_full_name(),user.id,invited_user.id,rsvpSent.code), title="Wedding Invitation", subject="Wedding Invitation")

        # return HttpResponseRedirect('/rsvp/')

    elif request.method == 'POST':
        emails = request.POST.get('emails')
        print 'email',emails
        emails = emails.split(',')
        code = id_generator()
        for email in emails:
            friends = None

            print "Sending email to: ",email.strip()
            try:
                user_email_get =User.objects.filter(email=email).exists()
                rsvpSent = RsvpToEmails.objects.filter(user=user,invited_email=email).exists()
                if user_email_get:
                    email_exists = "%s is already associated with user on YapJoy. Kindly add the user on yapjoy and send invitation."%(email)
                elif rsvpSent:
                    rsvpSent = RsvpToEmails.objects.get(user=user,invited_email=email,status='Pending')
                    send_email(email, message="You have been invited by %s.<br/><br/>If you want to accept invitation,then kindly click link below.<br /><br /><a href='https://www.yapjoy.com/acceptedinvitation/%s/%s/%s'>ACCEPT</a>"%(request.user.get_full_name(),user.id,email,rsvpSent.code), title="%s Wedding Invitation"%(full_name), subject="Wedding Invitation")
                    success_message = "%s is invited again."%(email)
                else:
                    send_email(email, message="You have been invited by %s.<br/><br/>If you want to accept invitation,then kindly click link below.<br /><br /><a href='https://www.yapjoy.com/acceptedinvitation/%s/%s/%s'>ACCEPT</a>"%(request.user.get_full_name(),user.id,email,code), title="%s Wedding Invitation"%(full_name), subject="Wedding Invitation")
                    print 'email is sent'
                    rsvpSent = RsvpToEmails.objects.create(user=user,invited_email=email,code=code,status='Pending')
                    try:
                        rsvpCount=RsvpCount.objects.get(user=user)
                        rsvpCount.rsvp_count += 1
                        rsvpCount.save()

                    except:
                        RsvpCount.objects.create(user=user,rsvp_count=1)
                            # context = {
                    #     'all_friends':all_friends,
                    #     'rsvpUserSent':rsvpUserSent,
                    #     'rsvpAccepted':rsvpAccepted,
                    #     'rsvpEmails':rsvpEmails,
                    #     'email_exists':email_exists,
                    #             }
                    # return render(request, 'vendroid/market/rsvp.html', context)

            except:
                pass



    context = {
        'all_friends':all_friends,
        'rsvpUserSent':rsvpUserSent,
        'rsvpAccepted':rsvpAccepted,
        'rsvpEmails':rsvpEmails,
        'rsvpEmails':rsvpEmails,
        'success_message':success_message,
        'email_exists':email_exists,
    }



    return render(request, 'vendroid/market/rsvp.html', context)
def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def invite_user(request,id):
    print 'here',id
    user = request.user
    print user.email
    profile = user.userprofile
    if profile.type == UserProfile.PROFESSIONAL or profile.type == UserProfile.OTHER:
        raise Http404
    try:
        print 'in try'
        invited_user = User.objects.get(id=id)
        code = id_generator()
        print 'code',code

        print 'sent  email',invited_user.email
        rsvpCount = None
        rsvpCountCreated = None
        rsvpSent = None
        try:
            rsvpCount=RsvpCount.objects.get(user=user)
        except:
            rsvpCount=RsvpCount.objects.create(user=user,rsvp_count=1)
            rsvpCountCreated = True

        try:
            rsvpSent = RsvpSend.objects.get(user=user,invited_user=invited_user,status='Pending')
        except:
            rsvpSent = RsvpSend.objects.create(user=user,invited_user=invited_user,code=code,status='Pending')
            if not rsvpCountCreated:
                rsvpCount.rsvp_count += 1
                rsvpCount.save()
        send_email(invited_user.email, message="You have been invited by %s.<br/><br/>If you want to accept invitation,then kindly click link below.<br /><br /><a target='_blank' href='https://www.yapjoy.com/invitationaccepted/%s/%s/%s'>ACCEPT INVITATION</a>"%(request.user.get_full_name(),user.id,invited_user.id,rsvpSent.code), title="Wedding Invitation", subject="Wedding Invitation")

        # return HttpResponseRedirect('/rsvp/')
        errormessage = "Your invitation has send."
        context = {
        'errormessage':errormessage,
        }
        return render(request, 'vendroid/market/rsvp_invitation_message.html',context)
    except Exception as e:
        print 'eccd', e
        errormessage = "Sorry! Your invitation has not send."
        context = {
        'errormessage':errormessage,
    }

        return render(request, 'vendroid/market/rsvp_invitation_message.html',context)

def acceptRsvp(request,userid,invitedid,code):
    print 'here',userid
    user = User.objects.get(id=userid)
    invited_user = User.objects.get(id=invitedid)
    rsvpSent = RsvpSend.objects.get(user=user,invited_user=invited_user,code=code)
    if not rsvpSent.status == 'Accepted':
        rsvpSent.status = 'Accepted'
        rsvpSent.save()
        rsvpCount=RsvpCount.objects.get(user=user)
        rsvpCount.rsvp_accepted_count += 1
        rsvpCount.save()
    # else:
    #     raise Http404


    errormessage = "Thank you for accepting the invitation."
    context = {
    'errormessage':errormessage,
        }

    return render(request, 'vendroid/market/email_friend_invitation.html',context)

def acceptRsvpEmail(request,userid,email,code):
    print 'here',userid
    print 'here',email
    print 'here',code
    user = User.objects.get(id=userid)
    try:
        rsvpSent = RsvpToEmails.objects.get(user=user,invited_email=email,code=code,status='Pending')
        rsvpSent.status = 'Accepted'
        rsvpSent.save()
        rsvpCount=RsvpCount.objects.get(user=user)
        rsvpCount.rsvp_accepted_count += 1
        rsvpCount.save()
    except:
        raise Http404


    errormessage = "Thank you for accepting the invitation."
    context = {
    'errormessage':errormessage,
        }

    return render(request, 'vendroid/market/email_friend_invitation.html',context)


@login_required(login_url='/login/')
@csrf_exempt
def marketV2(request, id):
    user = request.user
    profile = user.userprofile
    product = Product.objects.get(id=id)

    subBudgets = ProductBudget.objects.filter(product=product).select_related('product').order_by('created_at')
    sumBudget = subBudgets.aggregate(Sum('budget'))['budget__sum']
    leftBudget = product.amount - sumBudget

    if profile.type == UserProfile.PROFESSIONAL or profile.type == UserProfile.OTHER:
        raise Http404

    if request.method == 'POST':
        if 'totalAmount' in request.POST:
            totalAmount = request.POST.get('totalAmount')
            id = request.POST.get('id')
            print totalAmount, id

            product = Product.objects.get(id=id)
            product.amount = totalAmount
            product.save()

            return HttpResponse("success")

        elif 'productNote' in request.POST:
            productNote = request.POST.get('productNote').lstrip().rstrip()
            id = request.POST.get('id')
            print productNote, id

            product = Product.objects.get(id=id)
            product.description = productNote
            product.save()
            return HttpResponse("success")

        else :
            budget = request.POST.get('budget')
            title = request.POST.get('title')

            newBudget = ProductBudget.objects.create(product_id=id,
                                         title=title,
                                         budget=budget,
                                         is_awarded=False
                                         )

            subBudgets = ProductBudget.objects.filter(product=product).select_related('product').order_by('created_at')
            sumBudget = subBudgets.aggregate(Sum('budget'))['budget__sum']
            leftBudget = product.amount - sumBudget
            dictBudget = {sub.id: sub.budget for sub in subBudgets}
            context = {
                'subBudgets': subBudgets,
                'totalAmount': product.amount,
                'dictBudget': dictBudget,
                'sumBudget': sumBudget,
                'leftBudget': leftBudget
            }

            return render(request, 'vendroid/market/_subBudgetsV2.html', context)

    dictBudget = {sub.id: sub.budget for sub in subBudgets}

    productBudgetForm = ProductBudgetForm()
    print "product amont", product.amount
    context = {
        'form': productBudgetForm,
        'product':product,
        'subBudgets': subBudgets,
        'leftBudget': leftBudget,
        'sumBudget': sumBudget,
        'totalAmount': product.amount,
        'dictBudget': dictBudget
    }
    return render(request, 'vendroid/market/marketV2.html', context)

@login_required(login_url='/login/')
@csrf_exempt
def awardSubBudget(request):
    if request.is_ajax():
        id = request.POST.get('id')
        print 'ID: ',id
        user = request.user
        subBudget = ProductBudget.objects.get(id=id)
        print subBudget
        print subBudget.is_awarded

        if subBudget.is_awarded:
            subBudget.is_awarded = False
            subBudget.save()
            print "not"
            return HttpResponse('notAwarded')
        else:
            subBudget.is_awarded = True
            subBudget.save()
            print "yes"
            return HttpResponse('awarded')

    else:
        print "Failed"
        return HttpResponse('Failed')

@login_required(login_url='/login/')
@csrf_exempt
def changebudget(request):
    if request.is_ajax():
        id = request.POST.get('id')
        budget = request.POST.get('budget')
        title = request.POST.get('title')
        print 'ID: ',id, budget, title

        subBudget = ProductBudget.objects.get(id=id)
        # print subBudget.budget

        subBudget.budget = budget
        subBudget.title = title
        subBudget.save()

        # print subBudget.budget

        return HttpResponse('success')
    else:
        print "Failed"
        return HttpResponse('Failed')

@login_required(login_url='/login/')
@csrf_exempt
def deletebudget(request):
    if request.is_ajax():
        id = request.POST.get('id')
        productId = request.POST.get('productId')

        product = Product.objects.get(id=productId)
        subBudget = ProductBudget.objects.get(id=id)
        subBudget.delete()

        subBudgets = ProductBudget.objects.filter(product=product).select_related('product').order_by('created_at')
        sumBudget = subBudgets.aggregate(Sum('budget'))['budget__sum']
        leftBudget = product.amount - sumBudget
        dictBudget = {sub.id: sub.budget for sub in subBudgets}
        context = {
            'subBudgets': subBudgets,
            'totalAmount': product.amount,
            'dictBudget': dictBudget,
            'sumBudget': sumBudget,
            'leftBudget': leftBudget
        }

        return render(request, 'vendroid/market/_subBudgetsV2.html', context)

    else:
        print "Failed"
        return HttpResponse('Failed')

@login_required(login_url='/login/')
@csrf_exempt
def changeTotalAmount(request):
    if request.is_ajax():
        totalAmount = request.POST.get('totalAmount')
        id = request.POST.get('id')

        product = Product.objects.get(id=id)
        product.amount = totalAmount
        product.save()

        return HttpResponse('success')

    else:
        print "Failed"
        return HttpResponse('Failed')



# @login_required(login_url='/login/')
@csrf_exempt
def question(request, option_search_id, product_id, user_id):
    user = User.objects.get(id=user_id)  # request.user
    option_id_forward = option_search_id
    questions = ProductQuestion.objects.filter(option_search__id=option_search_id).order_by("-questionSequence")
    if not questions:
        return HttpResponse('No questions available')
    # totalOptions = ProductQuestionOption.objects.filter(question__in=questions).order_by("created_at")
    totalOptions = [ProductQuestionOption.objects.filter(question=q).order_by("created_at") for q in questions]
    index = 0
    isFinish = False
    for q in questions:
        if ProductAnswer.objects.filter(product__id=product_id, product_question=q).exists():
            index += 1
        if index == questions.count() - 1:
            isFinish = True
            print 'is finished = true'
    if not index == 0:
        index = index - 1
    print "questions", questions
    print "totalOptions", totalOptions

    #save the question answer
    if request.method == "POST":
        #Forward/Next Question
        if "answer" in request.POST:
            print "forward here"
            index = request.POST.get('index')
            answer = request.POST.get('answer')
            questionId = request.POST.get('questionId')

            print "answer", answer
            print "forward index", index
            print "questionID", questionId

            index = int(index)
            isFinish = False
            if index > questions.count() - 1:
                isFinish = True
                sendQuestion = []
                sendOption = []

                # return HttpResponseRedirect("/answer/"+name+"/")
            elif index == questions.count() - 1:
                isFinish = True
                sendQuestion = questions[index]
                sendOption = totalOptions[index]
            else:
                sendQuestion = questions[index]
                sendOption = totalOptions[index]

            # answer = ", ".join([item for item in answer])
            try:
                p_answer = ProductAnswer.objects.get(product__id=product_id,
                                                     user=user,
                                                     product_question=questionId)
                p_answer.answer = answer
                p_answer.save()
            except:
                ProductAnswer.objects.create(product_id=product_id,
                                             user=user,
                                             product_question_id=questionId,
                                             answer=answer
                                             )


            context = {
                'question': sendQuestion,
                'options': sendOption,
                'index': index,
                'isFinish': isFinish,
                'product_id': product_id,
                'option_id_forward': option_id_forward,
                'user_id': user_id,
            }
            # print "forward or backward", context
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        #Back Question
        elif "index" in request.POST:
            index = request.POST.get('index')
            index = int(index)
            # print "back index", index
            if questions:
                questions = questions[index]
            context = {
                'question': questions,
                'options': totalOptions[index],
                'index': index,
                'isFinish': False,
                'product_id': product_id,
                'option_id_forward': option_id_forward,
                'user_id': user_id,
            }
            # print "forward or backward", context
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        else:
            return Http404
    print 'option search id:',option_search_id
    if questions:
        questions = questions[index]
    context = {
        'question':questions,
        'options': totalOptions[index],
        'index': index,
        'isFinish': isFinish,
        'user_id': user_id,
        'product_id': product_id,
        'option_id_forward': option_id_forward,
    }

    # print "context", context
    return render(request, 'vendroid/demov2/market/question/question.html', context)


@login_required(login_url='/login/')
@csrf_exempt
def question_req(request, option_search_id, product_id):
    user = request.user
    option_id_forward = option_search_id
    totalquestionCount = ProductQuestion.objects.filter(option_search__id=option_search_id).count()
    print "totalquestionCount", totalquestionCount

    #save the question answer
    if request.method == "POST":
        #Forward/Next Question
        if "answer" in request.POST:
            index = request.POST.get('index')
            answer = request.POST.get('answer')
            questionId = request.POST.get('questionId')

            print "answer", answer
            print "forward index", index
            print "questionID", questionId
            p_answer = None
            # answer = ", ".join([item for item in answer])
            try:
                p_answer = ProductAnswer.objects.get(product__id=product_id,
                                                     user=user,
                                                     product_question=questionId)
                p_answer.answer = answer
                p_answer.save()
            except:
                p_answer = ProductAnswer.objects.create(product_id=product_id,
                                             user=user,
                                             product_question_id=questionId,
                                             answer=answer
                                             )
            """
            handle indexing
            """
            #Use index as question sequence to query
            try:
                # seqFirst += 1
                sendQuestion = ProductQuestion.objects.get(option_search__id=option_search_id, questionSequence=index)
                sendOption = ProductQuestionOption.objects.filter(question=sendQuestion).order_by("created_at")
            except:
                sendQuestion = []
                sendOption = []

            isFinish = False
            print "seqFirst Next", index, totalquestionCount, isFinish
            if int(index)+1 >= int(totalquestionCount):
                isFinish = True
            print int(index), int(totalquestionCount)
            print "seqFirst Next", index, totalquestionCount, isFinish

            print "after seqFirst Next", index, totalquestionCount, isFinish
            context = {
                'question': sendQuestion,
                'options': sendOption,
                'index': index,
                'isFinish': isFinish,
                'product_id': product_id,
                'option_id_forward': option_id_forward,
                'user_id': user.id,
                'product': p_answer.product,
            }
            # print "forward"
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        #Back Question
        elif "backIndex" in request.POST:
            index = request.POST.get('backIndex')
            index = int(index)

            #use index to query
            try:
                questionsBack = ProductQuestion.objects.get(option_search__id=option_search_id, questionSequence=index)
                optionBack = ProductQuestionOption.objects.filter(question=questionsBack).order_by("created_at")
            except:
                questionsBack = []
                optionBack = []

            print "seqFirst back", index

            context = {
                'question': questionsBack,
                'options': optionBack,
                'index': index,
                'isFinish': False,
                'product_id': product_id,
                'option_id_forward': option_id_forward,
                'user_id': user.id,
            }
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        else:
            return Http404

    #Find the first not answered question
    questions = ProductQuestion.objects.prefetch_related('productanswer_set').filter(option_search_id=option_search_id).order_by("questionSequence")
    if not questions:
        return HttpResponse('No questions available')
    questions_answers = ProductQuestion.objects.prefetch_related('productanswer_set').filter(productanswer__isnull=True,
                                                                                     option_search__id=option_search_id).order_by(
        "questionSequence")
    #print 'answers are: ',ProductAnswer.objects.filter(product_id=product_id, product_question__in=questions).count()
    if totalquestionCount <= ProductAnswer.objects.filter(product_id=product_id, product_question__in=questions).count():
        return HttpResponseRedirect('/answer/%s/%s/%s/'%(option_search_id, product_id, user.id))
    questionFirst = questions[0]
    totalOptionsFirst = ProductQuestionOption.objects.filter(question=questionFirst).order_by("created_at")

    #Deal with the case if last question not answered
    leftCount = questions.count()
    if leftCount == 1: isLast = True
    else: isLast = False

    context = {
        'question': questionFirst,
        'options': totalOptionsFirst,
        'index': questionFirst.questionSequence,
        'isFinish': False,
        'user_id': user.id,
        'product_id': product_id,
        'option_id_forward': option_id_forward,
        'isLast': isLast
    }

    # print "context", context
    return render(request, 'vendroid/demov2/market/question/question.html', context)



@login_required(login_url='/login/')
@csrf_exempt
def question_general(request):
    user = request.user
    # option_id_forward = option_search_id
    gen_cat = optionsSearch.objects.get(name="General Questions")
    gen_cat_id = gen_cat.id
    product = Product.objects.get_or_create(user=request.user, title="General Questions", category=gen_cat)[0]
    product_id = product.id
    totalquestionCount = ProductQuestion.objects.filter(option_search_id=gen_cat_id).count()
    print "totalquestionCount", totalquestionCount

    #save the question answer
    if request.method == "POST":
        #Forward/Next Question
        if "answer" in request.POST:
            index = request.POST.get('index')
            answer = request.POST.get('answer')
            questionId = request.POST.get('questionId')

            print "answer", answer
            print "forward index", index
            print "questionID", questionId

            # answer = ", ".join([item for item in answer])
            try:
                p_answer = ProductAnswer.objects.get(product__id=product_id,
                                                     user=user,
                                                     product_question=questionId)
                p_answer.answer = answer
                p_answer.save()
            except:
                ProductAnswer.objects.create(product_id=product_id,
                                             user=user,
                                             product_question_id=questionId,
                                             answer=answer
                                             )
            """
            handle indexing
            """
            #Use index as question sequence to query
            try:
                # seqFirst += 1
                sendQuestion = ProductQuestion.objects.get(option_search__id=gen_cat_id, questionSequence=index)
                sendOption = ProductQuestionOption.objects.filter(question=sendQuestion).order_by("created_at")
            except:
                sendQuestion = []
                sendOption = []

            isFinish = False
            print "seqFirst Next", index, totalquestionCount, isFinish
            if int(index)+1 >= int(totalquestionCount):
                isFinish = True
            print int(index), int(totalquestionCount)
            print "seqFirst Next", index, totalquestionCount, isFinish

            print "after seqFirst Next", index, totalquestionCount, isFinish
            context = {
                'question': sendQuestion,
                'options': sendOption,
                'index': index,
                'isFinish': isFinish,
                'isGeneral': True,

                'product_id': product_id,
                'option_id_forward': gen_cat_id,
                'user_id': user.id,
            }
            # print "forward"
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        #Back Question
        elif "backIndex" in request.POST:
            index = request.POST.get('backIndex')
            index = int(index)

            #use index to query
            try:
                questionsBack = ProductQuestion.objects.get(option_search__id=gen_cat_id, questionSequence=index)
                optionBack = ProductQuestionOption.objects.filter(question=questionsBack).order_by("created_at")
            except:
                questionsBack = []
                optionBack = []

            print "seqFirst back", index

            context = {
                'question': questionsBack,
                'options': optionBack,
                'index': index,
                'isFinish': False,
                'product_id': product_id,
                'option_id_forward': gen_cat_id,
                'user_id': user.id,
            }
            return render(request, 'vendroid/demov2/market/question/_partial_question.html', context)

        else:
            return Http404

    #Find the first not answered question
    questions = ProductQuestion.objects.prefetch_related('productanswer_set').filter(option_search_id=gen_cat_id).order_by("questionSequence")
    if not questions:
        return HttpResponse('No questions available')
    # questions_answers = ProductQuestion.objects.prefetch_related('productanswer_set').filter(productanswer__isnull=True,
    #                                                                                  option_search__id=gen_cat_id).order_by(
    #     "questionSequence")
    # if not questions_answers:
    #     return HttpResponseRedirect('/answer/%s/%s/%s/'%(gen_cat_id, product_id, user.id))
    questionFirst = questions[0]
    totalOptionsFirst = ProductQuestionOption.objects.filter(question=questionFirst).order_by("created_at")

    #Deal with the case if last question not answered
    leftCount = questions.count()
    if leftCount == 1: isLast = True
    else: isLast = False

    context = {
        'question': questionFirst,
        'options': totalOptionsFirst,
        'index': questionFirst.questionSequence,
        'isFinish': False,
        'user_id': user.id,
        'product_id': product_id,
        'option_id_forward': gen_cat_id,
        'isLast': isLast
    }

    # print "context", context
    return render(request, 'vendroid/demov2/market/question/question.html', context)


# @login_required(login_url='/login/')
@csrf_exempt
def answer(request, option_search_id, product_id, user_id):
    user = User.objects.get(id=user_id)#request.user
    gen_cat = optionsSearch.objects.get(name="General Questions")
    product_general_question = Product.objects.get_or_create(user=request.user, title="General Questions", category=gen_cat)[0]
    general_questions = ProductQuestion.objects.filter(Q(option_search__name='General Questions')).order_by("-id")
    general_answers = ProductAnswer.objects.select_related('product').filter(product_id=product_general_question.id, user=user,
                                                                     product_question__in=general_questions).order_by(
        "-product_question_id")
    zipped_answers_general = zip(general_questions, general_answers)
    questions = ProductQuestion.objects.filter(Q(option_search__id=option_search_id)).order_by("-id")

    answers = ProductAnswer.objects.select_related('product').filter(product__id=product_id, user=user, product_question__in=questions).order_by("-product_question_id")
    product = Product.objects.get(id=product_id)
    zipped_answers = zip(questions, answers)
    print "zipped_answers", zipped_answers
    if not answers:
        return HttpResponse('No answers available')

    # save the question answer
    if request.method == "POST":
        #get question options for pop up dialog
        if "questionId" in request.POST:
            questionId = request.POST.get('questionId')
            q = ProductQuestion.objects.get(id=questionId)
            productOptions = ProductQuestionOption.objects.filter(question__id=questionId).order_by("created_at")
            isGeneralQuestion = False
            print q.option_search.name
            if q.option_search.name == "General Questions":
                isGeneralQuestion = True
            print isGeneralQuestion
            context = {
                'question': q,
                'options': productOptions,
                'isGeneralQuestion': isGeneralQuestion,
            }
            print "answer dialog", context
            return render(request, 'vendroid/demov2/market/question/_partial_dialog_question.html', context)

        #saving answer from dialog modal
        elif "answer" in request.POST:
            print request.POST
            answer = request.POST.get('answer')
            id = request.POST.get('id')
            print "answer, save", answer, id, product_id
            print "prouct id: ", product_id
            print "prouct question id: ", id

            if "genQues" in request.POST:
                try:
                    print 'updatng answer general'
                    print id, user, product_general_question.id
                    p_answer = ProductAnswer.objects.get(product_id=product_general_question.id, user=user, product_question=id)
                    p_answer.answer = answer
                    p_answer.save()
                    print p_answer.id
                except Exception as e:
                    print e
                    # ProductAnswer.objects.create(product_id=product_id,
                    #                              user=user,
                    #                              product_question_id=id,
                    #                              answer=answer
                    #                              )
            else:
                try:
                    print 'updatng answer'
                    p_answer = ProductAnswer.objects.get(product_id=product_id, user=user, product_question=id)
                    p_answer.answer = answer
                    p_answer.save()
                    print p_answer.id
                except Exception as e:
                    print e
                    # ProductAnswer.objects.create(product_id=product_id,
                    #                              user=user,
                    #                              product_question_id=id,
                    #                              answer=answer
                    #                              )

            # return JsonResponse({'answer': answer})
            return HttpResponse("success")

    context = {
        'zipped_answers': zipped_answers,
        'zipped_answers_general': zipped_answers_general,
        'product': product,
    }
    return render(request, 'vendroid/demov2/market/question/answer.html', context)

# @login_required(login_url='/login/')
@csrf_exempt
def dream(request, id):
    # user = request.user
    dreams = Dream.objects.select_related('product').filter(product_id=id,
                                                            # product__user=user
                                                            ).order_by("-created_at")

    for d in dreams:
        print d.image.url

    if request.method == 'POST':
        formData = dreamImageForm(request.POST, request.FILES)
        if formData.is_valid():
            image = formData.cleaned_data['image']

            #If user can only create one product for each category!!! TODO: may need fix
            product = Product.objects.get(id=id,
                                          # user=user
                                          )
            Dream.objects.create(product=product, image=image)

            newDreams = Dream.objects.select_related('product').filter(product=product).order_by("-created_at")

            context = {
                'dreams': newDreams,
            }
            return render(request, 'vendroid/demov2/dream/_partial_dream.html', context)

    context = {
        'dreams': dreams,
    }
    return render(request, 'vendroid/demov2/dream/dream.html', context)


@login_required(login_url='/loginv3/')
@csrf_exempt
def dream_req(request, id):
    user = request.user
    send_publishing = None
    send_publishing_error = None
    product = Product.objects.get(id=id, user=request.user)
    dreams = Dream.objects.select_related('product').filter(product_id=id,
                                                            product__user=user
                                                            ).order_by("-created_at")

    for d in dreams:
        print d.image.url
    switch = 1
    list1 = []
    list2 = []
    list3 = []
    for d in dreams:
        if switch == 1:
            list1.append({
                'image':d.image,
                'description':d.description,
                'id':d.id,
            })
            switch = 2
            continue
        if switch == 2:
            list2.append({
                'image':d.image,
                'description':d.description,
                'id': d.id,
            })
            switch = 3
            continue
        if switch == 3:
            list3.append({
                'image':d.image,
                'description':d.description,
                'id': d.id,
            })
            switch = 1
            continue

    if 'publish' in request.POST:
        totalquestionCount = ProductQuestion.objects.filter(option_search__id=product.category_id).count()
        questions_pass = ProductQuestion.objects.prefetch_related('productanswer_set').filter(
            option_search_id=product.category_id).order_by("questionSequence")
        if totalquestionCount <= ProductAnswer.objects.filter(product_id=product.id, product_question__in=questions_pass).count():
            print ' i m published'
            product.status=Product.ACTIVE
            product.isListing = True
            product.save()
            send_publishing = "Your plan is published"
        else:
            send_publishing_error = "Plans are not yet completed."
    elif request.method == 'POST':
        print request.POST
        formData = dreamImageForm(request.POST, request.FILES)
        if formData.is_valid():
            image = formData.cleaned_data['image']
            print request.POST
            print image
            description = request.POST['description']

            #If user can only create one product for each category!!! TODO: may need fix
            product = Product.objects.get(id=id,
                                          user=user
                                          )
            Dream.objects.create(product=product, image=image, description=description)

            newDreams = Dream.objects.select_related('product').filter(product=product).order_by("-created_at")
            # for d in newDreams:
            #     print d.image.url
            switch = 1
            list1 = []
            list2 = []
            list3 = []
            for d in newDreams:
                if switch == 1:
                    list1.append({
                        'image': d.image,
                        'description': d.description,
                        'id': d.id,
                    })
                    switch = 2
                    continue
                if switch == 2:
                    list2.append({
                        'image': d.image,
                        'description': d.description,
                        'id': d.id,
                    })
                    switch = 3
                    continue
                if switch == 3:
                    list3.append({
                        'image': d.image,
                        'description': d.description,
                        'id': d.id,
                    })
                    switch = 1
                    continue
            context = {
                'dreams': newDreams,
                'list1': list1,
                'list2': list2,
                'list3': list3,
                'product': product,
            }
            return render(request, 'vendroid/demov2/dream/_partial_dream.html', context)
    # if "update_desc" in request.is_ajax():
        # pass
    if "dashboardlink" in request.POST:
        print 'inside dashboard link'

        dashboard_link = request.POST.get('dashboardlink')
        product.dashboard_link = dashboard_link
        product.save()
        print product.dashboard_link
    if request.is_ajax():
        if "update_desc" in request.POST:
            desc = request.POST.get('update_desc')
            if desc:
                product.description = desc
                product.save()
                return HttpResponse('done')
        elif "delete_image" in request.POST:
            dream_delete = None
            delete_image = request.POST.get('delete_image')
            print 'delete image: ',delete_image
            try:
                dream_delete = Dream.objects.get(id=delete_image, product__user_id=user.id)
                dream_delete.delete()
                return HttpResponse('Done')
            except:
                return HttpResponse('Failed')
        elif "image-desc-edit" in request.POST:
            image_desc_edit = request.POST.get('image-desc-edit')
            description_edit = request.POST.get('description-edit')
            print image_desc_edit, description_edit
            print 'returning done'
            try:
                dream_edit = Dream.objects.get(id=image_desc_edit, product__user_id=user.id)
                dream_edit.description = description_edit
                dream_edit.save()
                return HttpResponse('Done')
            except:
                return HttpResponse('Failed')


    context = {
        'product': product,
        'dreams': dreams,
        'product': product,
        'list1': list1,
        'list2': list2,
        'list3': list3,
        'send_publishing': send_publishing,
        'send_publishing_error': send_publishing_error,
    }
    return render(request, 'vendroid/demov2/dream/dream.html', context)



@login_required(login_url='/login/')
@csrf_exempt
def questionAdmin(request):
    user = request.user
    categories = optionsSearch.objects.all().order_by("-created_at")
    questions = [ProductQuestion.objects.filter(option_search=c).order_by("questionSequence") for c in categories]

    """
    For displaying categories with questions with options
    """
    q_option_ary = []
    for q_set in questions:
        tmpAry = []
        for q in q_set:
            try:
                tmp = ProductQuestionOption.objects.filter(question=q)
            except:
                tmp = []

            tmpAry.append((q, tmp))

        q_option_ary.append(tmpAry)

        # print "tmp", tmp

    # print "ary", q_option_ary
    zip_question = zip(categories, q_option_ary)
    # print "zipped", zip_question

    # print "zip_q", zip_q
    one_question = ProductQuestion.objects.all().order_by("questionSequence")[0]
    one_question_options = ProductQuestionOption.objects.filter(question=one_question).order_by("-created_at")
    currCategory = one_question.option_search.name
    all_options = ProductQuestionOption.objects.all().order_by("-created_at")
    # print "one_question", one_question
    # print "question options", one_question_options

    if request.method == "POST":
        #View question
        if "viewQuestionId" in request.POST:
            q_id = request.POST.get("viewQuestionId")
            #if not add new question
            if int(q_id) > 0:
                p_Q = ProductQuestion.objects.get(id=q_id)
                one_question_options = ProductQuestionOption.objects.filter(question=p_Q).order_by("-created_at")
                currCategory = p_Q.option_search.name
                p_Qid = p_Q.id
            else:
                p_Q = []
                p_Qid = 0
                one_question_options = []

            context = {
                'categories': categories,
                'one_question': p_Q,
                'one_question_id': p_Qid,
                'one_question_options': one_question_options,
                'all_options':all_options,
                'currCategory': currCategory
            }
            return render(request, 'vendroid/market/question/Admin/_partial_questions_panel.html', context)


        # Delete question
        elif "removeQuestionId" in request.POST:
            q_id = request.POST.get("removeQuestionId")
            p_Q = ProductQuestion.objects.get(id=q_id)
            p_Q.delete()

            #Re-generate data
            questions = [ProductQuestion.objects.filter(option_search=c).order_by("questionSequence") for c in categories]
            q_option_ary = []
            for q_set in questions:
                tmpAry = []
                for q in q_set:
                    try:
                        tmp = ProductQuestionOption.objects.filter(question=q)
                    except:
                        tmp = []

                    tmpAry.append((q, tmp))

                q_option_ary.append(tmpAry)

            # print "ary", q_option_ary
            zip_question = zip(categories, q_option_ary)
            context = {
                'zipped_questions': zip_question,
            }
            return render(request, 'vendroid/market/question/Admin/_partial_questions_list.html', context)

        #Remove existing option form certain question
        elif "deleteOptionQuestionId" in request.POST:
            deleteOptionQuestionId = request.POST.get("deleteOptionQuestionId")
            optionId = request.POST.get("optionId")

            pQ = ProductQuestion.objects.get(id=deleteOptionQuestionId)
            option = ProductQuestionOption.objects.get(id=optionId)
            pQ.options.remove(option)
            option.question.remove(pQ)

            one_question_options = ProductQuestionOption.objects.filter(question=pQ).order_by("-created_at")

            context = {
                "one_question_options":one_question_options,
                "all_options": all_options
            }
            return render(request, 'vendroid/market/question/Admin/_partial_answers.html', context)

        #Change existing option in panel
        elif "updateOptionQuestionId" in request.POST:
            print 'inside upadte section'
            changeOptionQuestionId = request.POST.get("updateOptionQuestionId")
            oldOptionId = request.POST.get("oldOptionId")
            newOptionId = request.POST.get("newOptionId")
            allowedDateTime = request.POST.get("allowedDateTime")
            allowedTextArea = request.POST.get("allowedTextArea")

            pQ = ProductQuestion.objects.get(id=changeOptionQuestionId)
            oldOption_obj = ProductQuestionOption.objects.get(id=oldOptionId)
            newOption_obj = ProductQuestionOption.objects.get(id=newOptionId)

            #changing the old and new options
            pQ.options.remove(oldOption_obj)
            pQ.options.add(newOption_obj)
            oldOption_obj.question.remove(pQ)
            newOption_obj.question.add(pQ)

            #update the properties
            isDate = False
            isText = False
            if allowedDateTime == "1":
                isDate = True
            else:
                isDate = False

            if allowedTextArea == "1":
                isText = True
            else:
                isText = False

            newOption_obj.isTextArea = isText
            newOption_obj.isDateTime = isDate
            newOption_obj.save()

            one_question_options = ProductQuestionOption.objects.filter(question=pQ).order_by("-created_at")

            context = {
                "one_question_options": one_question_options,
                "all_options": all_options
            }
            return render(request, 'vendroid/market/question/Admin/_partial_answers.html', context)

            # Re-generate data
            # questions = [ProductQuestion.objects.filter(option_search=c).order_by("questionSequence") for c in categories]
            # q_option_ary = []
            # for q_set in questions:
            #     tmpAry = []
            #     for q in q_set:
            #         try:
            #             tmp = ProductQuestionOption.objects.filter(question=q)
            #         except:
            #             tmp = []
            #
            #         tmpAry.append((q, tmp))
            #
            #     q_option_ary.append(tmpAry)
            #
            # # print "ary", q_option_ary
            # zip_question = zip(categories, q_option_ary)
            # context = {
            #     'zipped_questions': zip_question,
            # }
            #
            # return render(request, 'vendroid/market/question/Admin/_partial_questions_list.html', context)


        #Add a new option for this question
        elif "AddOptionQuestionId" in request.POST:
            print 'inside add option id'
            newOption = request.POST.get("newOption")
            questionId = int(request.POST.get("AddOptionQuestionId"))
            isNew = request.POST.get("isNew")
            category = request.POST.get("category")
            title = request.POST.get("title")
            allowedDateTime = request.POST.get("allowedDateTime")
            allowedTextArea = request.POST.get("allowedTextArea")
            print questionId, category, newOption, isNew
            currCategory = optionsSearch.objects.get(name__icontains=category)

            if allowedDateTime == "1": isDate = True
            else: isDate = False

            if allowedTextArea == "1": isText = True
            else: isText = False

            if questionId > 0:
                q = ProductQuestion.objects.get(id=questionId)
            else:
                #dummy created first
                q = ProductQuestion.objects.create(option_search=currCategory, title=title)

            if isNew == "1":
                option = ProductQuestionOption.objects.create(option=newOption, isDateTime=isDate, isTextArea=isText)
                option.question.add(q)
                q.options.add(option)

            else:
                print q.title
                #Add M2M key to qusetion_option
                q_option = ProductQuestionOption.objects.get(option__contains=newOption)
                q_option.isDatetime = isDate
                q_option.isTextArea = isText
                q_option.question.add(q)

                #Add M2M key to question
                q.options.add(q_option)


            one_question_options = ProductQuestionOption.objects.filter(question=q).order_by("-created_at")
            print one_question_options

            context = {
                'categories': categories,
                'one_question': q,
                'one_question_id': q.id,
                'one_question_options': one_question_options,
                'all_options': all_options,
                'currCategory': category
            }
            return render(request, 'vendroid/market/question/Admin/_partial_questions_panel.html', context)

            # context = {
            #     'one_question_options': one_question_options,
            #     'all_options': all_options,
            #     'one_question_id': q.id,
            # }
            # return render(request, 'vendroid/market/question/Admin/_partial_answers.html', context)


        # Edit question
        elif "saveQuestionId" in request.POST:
            print 'savequestionid'
            questionId = request.POST.get("saveQuestionId")
            category = request.POST.get("category")
            title = request.POST.get("title")
            allowedMultiple = request.POST.get("allowedMultiple")
            allowedDateTime = request.POST.get("allowedDateTime")
            allowedTextArea = request.POST.get("allowedTextArea")
            importance = int(request.POST.get("importance"))
            print "questionId", questionId
            print "dt and ta value: ",allowedDateTime, allowedTextArea


            category = optionsSearch.objects.get(name__icontains=category)
            if allowedMultiple == "1":
                isMulti = True
            else:
                isMulti = False

            if int(questionId) > 0:
                pQ = ProductQuestion.objects.get(id=questionId)

                pQ.option_search = category
                pQ.title = title
                pQ.isAllowMulti = isMulti
                pQ.questionSequence = importance
                pQ.save()

                print pQ.title
            else:
                # Add M2M key to qusetion_option
                q_option = ProductQuestion.objects.create(option_search=category,
                                                          questionSequence=importance,
                                                          isAllowMulti=isMulti,
                                                          title=title
                                                          )

                # for o in optionIds:
                #     p = ProductQuestionOption.objects.get(id=o)
                #     q_option.options.add(p)

            # Re-generate data
            questions = [ProductQuestion.objects.filter(option_search=c).order_by("questionSequence") for c in categories]
            q_option_ary = []
            for q_set in questions:
                tmpAry = []
                for q in q_set:
                    try:
                        tmp = ProductQuestionOption.objects.filter(question=q)
                    except:
                        tmp = []

                    tmpAry.append((q, tmp))

                q_option_ary.append(tmpAry)

            # print "ary", q_option_ary
            zip_question = zip(categories, q_option_ary)
            context = {
                'zipped_questions': zip_question,
            }

            return render(request, 'vendroid/market/question/Admin/_partial_questions_list.html', context)

        else:
            return Http404()


    context = {
        'zipped_questions': zip_question,
        'categories': categories,
        'one_question': one_question,
        'one_question_id': one_question.id,
        'one_question_options': one_question_options,
        'all_options': all_options,
        'currCategory': currCategory
    }

    # print "context", context
    return render(request, 'vendroid/market/question/Admin/questionAdmin.html', context)
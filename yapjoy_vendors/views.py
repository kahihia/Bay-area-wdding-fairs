from django.shortcuts import render, HttpResponseRedirect, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from yapjoy_market.models import *
from yapjoy_messages.models import *
from yapjoy_registration.models import AllFriends, Friends, UserProfile, Company
from django.db.models import Q
from yapjoy_files.models import *
from django.template import RequestContext, loader
from .models import *
from .forms import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from yapjoy_registration.commons import send_email
from yapjoy_registration.forms import yelpForm
from django.contrib.admin.views.decorators import staff_member_required

from yapjoy_vendors.serializer import *
from rest_framework.decorators import api_view, permission_classes

@login_required(login_url='/login/')
@csrf_exempt
def dashboard(request, option_id):
    #Numbers of product intended to display
    # in the next click of lazy load
    N = 1
    option_search = optionsSearch.objects.get(id=option_id)
    products = Product.objects.select_related('user','user__userprofile').filter(isListing=True, category_id=option_id).order_by('-created_at')
    # print products

    sendProduct = products#[:N]
    if request.method == "POST":
        if "index" in request.POST:
            index = int(request.POST.get('index'))

            if (index+1)*N >= products.count():
                newSendProduct = products
            else:
                newSendProduct = products[:(index+1)*N]

            # print "post context", newSendProduct
            context = {
                'products': newSendProduct,
            }
            return render(request, 'vendroid/demov2/vendors/dashboard/_partial_product.html', context)
    product = None
    if sendProduct:
        product = sendProduct[0]
    context = {
        'products': sendProduct,
        'product': product,
        'option_search': option_search,
    }
    # print "total context", context
    return render(request, 'vendroid/demov2/vendors/dashboard/dashboard.html', context)

@login_required(login_url='/login/')
@csrf_exempt
def productlist(request, option_search_id):
    #Numbers of product intended to display
    # in the next click of lazy load
    # N =
    products = Product.objects.filter(category=option_search_id).exclude(user__userprofile__type=UserProfile.PROFESSIONAL).order_by('-created_at')
    N = products.count() - 1
    # print products

    sendProduct = products#[:N]
    if request.method == "POST":
        if "index" in request.POST:
            index = int(request.POST.get('index'))

            if (index+1)*N >= products.count():
                newSendProduct = products
            else:
                newSendProduct = products[:(index+1)*N]

            # print "post context", newSendProduct
            context = {
                'products': newSendProduct,
            }
            return render(request, 'vendroid/demov2/vendors/dashboard/_partial_product.html', context)


    context = {
        'products': sendProduct,
    }
    # print "total context", context
    return render(request, 'vendroid/demov2/vendors/dashboard/product.html', context)




@login_required(login_url='/login/')
@csrf_exempt
def productlist_req(request, product_id):
    #Numbers of product intended to display
    # in the next click of lazy load
    # N =
    product = Product.objects.get(id=product_id, user=request.user)#.exclude(user__userprofile__type=UserProfile.PROFESSIONAL).order_by('-created_at')
    biddings = ProductBids.objects.filter(product=product).order_by('created_at')
    biddings_number = biddings.count()
    print 'bidding count: ', biddings_number
    # N = products.count() - 1
    # # print products
    #
    # sendProduct = products#[:N]
    # if request.method == "POST":
    #     if "index" in request.POST:
    #         index = int(request.POST.get('index'))
    #
    #         if (index+1)*N >= products.count():
    #             newSendProduct = products
    #         else:
    #             newSendProduct = products[:(index+1)*N]
    #
    #         # print "post context", newSendProduct
    #         context = {
    #             'products': newSendProduct,
    #         }
    #         return render(request, 'vendroid/demov2/vendors/dashboard/_partial_product.html', context)
    #

    # Numbers of product intended to display
    # in the next click of lazy load
    if request.method == "POST":
        bid_id = request.POST.get('bid_id')
        print 'bidding-id: ',bid_id
        bid = biddings[int(bid_id)]
        if bid and biddings_number:
            # bids =
            user = bid.vendor
            up = user.userprofile
            profile__image__form = VendorProfileImageForm()
            videoForm = vendorVideoForm()
            try:
                comp = Company.objects.get(userprofile=up)
                company_name = comp.name
                description = comp.description
            except:
                company_name = ""
                description = ""
            try:
                packages = Package.objects.filter(user_id=user.id).order_by("-created_at")
            except:
                packages = []
            # Yelp's
            try:
                y_imageUrl = up.get_yelp_profile_image()
            except:
                y_imageUrl = ""
            try:
                y_descp = up.get_yelp_description()
            except:
                y_descp = ""
            zipped_images = []
            photos = []
            # Images
            try:
                albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
                try:
                    photos = VendorImage.objects.filter(album__in=albums).order_by("-created_at")
                except:
                    photos = []  # [[] * len(albums)]
                    # if photos and albums:
                    #     zipped_images = zip(albums, photos)
            except:
                zipped_images = []
            print "Zipped", zipped_images
            initial_yelp = {}
            if up.yelp_name and up.yelp_location_zip:
                initial_yelp = {
                    'yelp_name': up.yelp_name,
                    'yelp_location_zip': up.yelp_location_zip,
                }
            yelp_form = yelpForm(initial=initial_yelp)
            profile_image_form = None
            context = {
                'up': up,
                'bid': bid,
                'videoUrl': up.video,
                'description': description,
                'company_name': company_name,
                'packages': packages,
                'yelp_form': yelp_form,
                'yelp_description': y_descp,
                'yelp_image': y_imageUrl,
                'zipped_images': zipped_images,
                'photos': photos,
                'videoForm': videoForm,
                'profile': up,
                'profile__image__form': profile__image__form,
            }
        return render(request, 'vendroid/demov2/vendors/dashboard/_partial_productV2/_partial_profile.html', context)
    # print "total context", context
    context = {
        'biddings':biddings,
        'biddings_number':biddings_number,
        'product':product,
    }
    return render(request, 'vendroid/demov2/vendors/dashboard/productv2.html', context)





@login_required(login_url='/login/')
@csrf_exempt
def vendor_message(request, product_id, receiver_id):
    user = request.user
    profile = user.userprofile
    receiver = User.objects.get(id=receiver_id)
    form = messageForm()

    product = Product.objects.get(id=product_id)
    messages = VendorMessage.objects.filter(Q(product__id=product_id) & ((Q(sender=user) & Q(receiver__id=receiver_id)) | (Q(sender=receiver_id) & Q(receiver=user)))).order_by('created_at')
    # print "messages", messages

    #(4)Send the Message
    if request.method == "POST":
        # formData = messageForm(request.POST)
        # if formData.is_valid():
        #     data = formData.cleaned_data
        #     newMessage = data['message']

        if "message" in request.POST:
            newMessage = request.POST.get('message')
            print "newMessage", newMessage

            if profile.type == UserProfile.PROFESSIONAL:
                if profile.amount > 0:
                    profile.amount -= 1
                    profile.save()
                    print "have money"
                    VendorMessage.objects.create(sender=user, receiver_id=receiver_id, message=newMessage, product_id=product_id)
                    messages = VendorMessage.objects.filter(Q(product__id=product_id) & ((Q(sender=user) & Q(receiver__id=receiver_id)) | (Q(sender=receiver_id) & Q(receiver=user)))).order_by('created_at')

                    # Check if enough amount
                    if profile.type == UserProfile.PROFESSIONAL and profile.amount == 0:
                        isEnoughcredit = "0"
                    else:
                        isEnoughcredit = "1"

                    context = {
                         'all_threads': messages,
                         'isEnoughcredit': isEnoughcredit
                    }
                    return render(request, 'vendroid/demov2/vendors/message/conversation.html', context)
                else:
                    print "no money"
                    messages = {"You do not have sufficient credit to send messages."}
                    context = {
                        'all_threads': messages,
                        'isEnoughcredit': "0"
                    }
                    print context
                    return render(request, 'vendroid/demov2/vendors/message/conversation.html', context)

            else:
                VendorMessage.objects.create(sender=user, receiver_id=receiver_id, message=newMessage, product_id=product_id)
                messages = VendorMessage.objects.filter(Q(product__id=product_id) & ((Q(sender=user) & Q(receiver__id=receiver_id)) | (Q(sender=receiver_id) & Q(receiver=user)))).order_by('created_at')

                context = {
                    'all_threads': messages,
                    'isEnoughcredit': "1"
                }
                print "b/g context", messages
                return render(request, 'vendroid/demov2/vendors/message/conversation.html', context)
        else:
            return Http404()

    #Check if enough amount
    if profile.type == UserProfile.PROFESSIONAL and profile.amount == 0:
        isEnoughcredit = "0"
    else:
        isEnoughcredit = "1"

    content = {
        'form':form,
        'receiver': receiver.userprofile,
        'all_threads': messages,
        'isEnoughcredit': isEnoughcredit,
        'profile': profile,
        'user': user,
        # 'unknown_messages':unknown_messages,
        # 'source': request.GET.get('source', ''),
        # 'video_call_init': request.GET.get('video_call_init', ''),
        # 'followings':followings,
    }

    template_name = "vendroid/demov2/vendors/message/online_message.html"

    return render(request, "vendroid/demov2/vendors/message/online_message.html", content)


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
    return render(request, 'vendroid/demov2/vendors/question/answer.html', context)



# @login_required(login_url='/login/')
@csrf_exempt
def SelectStep(request):
    print 'id is: ',id
    user = request.user
    # dp =  DemoPlan.objects.get(user_id=id)
    if request.method == "POST":
        survey = request.POST.get('survey')
        print survey
        if survey:
            distinct_surveys = list()
            # map(lambda x: not x in distinct_surveys and distinct_surveys.append(x), survey.split(","))
            # print distinct_surveys
            for x in survey.split(','):
                print x
                if x:
                    distinct_surveys.append(int(x))
            print 'final: ',distinct_surveys
            opt_search = optionsSearch.objects.filter(id__in=distinct_surveys)
            redirect_id = None
            for o in opt_search:
                try:
                    prod = Product.objects.filter(category=o,
                                                   user=user)
                    if prod:
                        redirect_id = prod[0].id
                    else:
                        prod = Product.objects.create(category=o,
                                                      user=user,
                                                      title=o.name)
                        redirect_id = prod.id

                except Exception as e:
                    print e

                    prod = Product.objects.create(category=o,
                                           user=user,
                                           title=o.name)
                    redirect_id = prod.id
            return HttpResponseRedirect(reverse("PlansStepv2"))
        # if "venue" in distinct_surveys:
        #     dp.is_venue_done = True
        #     if 'dj' in distinct_surveys:
        #         dp.is_dj_done = True
        #     dp.save()
        #     return HttpResponseRedirect(reverse("PlansStep", kwargs={'id': id, 'type': 'venue'}))
        # if "dj" in distinct_surveys:
        #     dp.is_dj_done = True
        #     dp.save()
        #     return HttpResponseRedirect(reverse("PlansStep", kwargs={'id': id, 'type':'dj'}))
    options = optionsSearch.objects.filter(status=optionsSearch.SHOW)
    return render(request, 'vendroid/demov2/vendors/select_vendors.html',{
        'options':options,
                })




@login_required(login_url='/loginv3/')
@csrf_exempt
def dream_req(request, id, user_id):
    user = request.user
    send_publishing = None
    product = Product.objects.get(id=id, user_id=user_id)
    dreams = Dream.objects.select_related('product').filter(product_id=id,
                                                            product__user_id=user_id
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



    context = {
        'dreams': dreams,
        'product': product,
        'list1': list1,
        'list2': list2,
        'list3': list3,
        'send_publishing': send_publishing,
    }
    return render(request, 'vendroid/demov2/vendors/dream/dream.html', context)

@login_required(login_url='/login/')
@csrf_exempt
def ListingView(request):
    packages = None
    user = request.user
    profile = user.userprofile
    if not profile.is_approved:
        return HttpResponseRedirect(reverse('vendors__profile'))
    vendors = VendorRegistration.objects.get(user=user)
    vendors_listing = VendorViewProduct.objects.get_or_create(vendor=user)[0]
    listings_objects = None
    my_offers = None
    vendors_offers = ProductBids.objects.filter(vendor=user).count()
    if "myoffers" in request.GET:
        vendors_offers_ids = ProductBids.objects.filter(vendor=user).values_list('product_id',flat=True)
        listings_objects = Product.objects.filter(category=vendors.categories, isListing=True, id__in=vendors_offers_ids)
        my_offers = True
    else:
        listings_objects = Product.objects.filter(category=vendors.categories, isListing=True)
    if request.method == "POST":
        print request.POST
        if "add_id_viewed" in request.POST:
            add_id_viewed = request.POST.get('add_id_viewed')
            print 'add_id_viewed: ',add_id_viewed
            add_id_viewed = add_id_viewed.replace(' ','')
            if not add_id_viewed in vendors_listing.get_vendor_viewed_list():
                if vendors_listing.id_viewed:
                    vendors_listing.id_viewed = "%s%s,"%(vendors_listing.id_viewed,add_id_viewed)
                else:
                    vendors_listing.id_viewed = "%s," % (add_id_viewed)
                vendors_listing.save()
    # if not profile.subscribed:
    packages = SubscriptionPackages.objects.all()
    return render(request,
                  'vendroid/demov2/vendors/listing/listings.html',{
                        'listings_objects':listings_objects,
                        'vendors':vendors,
                        'vendors_listing':vendors_listing,
                        'user':user,
                        'profile':profile,
                        'packages':packages,
                        'my_offers':my_offers,
                        'vendors_offers':vendors_offers,
                  })


from yapjoy_accounts.forms import CreditCardDepositConfirmForm
from yapjoy_accounts.models import Transaction
import stripe
@login_required(login_url='/login/')
@csrf_exempt
def Subscription(request, id):
    print id
    error_message = ""
    package = get_object_or_404(SubscriptionPackages, id=id)
    form = CreditCardDepositConfirmForm()
    if request.method == "POST":
        form = CreditCardDepositConfirmForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print 'data: ',data
            stripe_token = request.POST.get('stripe_token')
            print stripe_token
            user = request.user

            response = None
            try:
                stripe.api_key = "sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0"#settings.STRIPE_SECRET_KEY
                stripe_customer = stripe.Customer.create(
                    email=user.email,
                    card=stripe_token
                )
                profile = user.userprofile
                profile.stripe_id = stripe_customer.id
                profile.save()
                print 'about to response'
                response = stripe.Charge.create(
                    amount=int(100) * int(package.amount),  # Convert dollars into cents
                    currency="usd",
                    customer=profile.stripe_id,
                    description=user.email,
                )
            except Exception as e:
                error_message = e
            if response:
                print response
                trans = Transaction.objects.create(user=user,amount=package.amount,
                                                   status=Transaction.COMPLETED,
                                                   transaction_id=response.stripe_id,
                                                   response=response)
                profile.subscribed = True
                profile.amount += package.tokens
                profile.save()
                send_email(user.email,
                           'Congratulations on your recent purchase of %s tokens.<br /><br /> It has been our pleasure to serve you.<br /><br /> If we can be of further assistance, please let us know at info@yapjoy.com.<br /><br />Best<br />YapJoy Team'%(package.tokens),
                           'Successful Purchase!'
                           , 'Successful Purchase!')
                send_email('adeel@yapjoy.com',
                           'Congratulations on your recent purchase of %s tokens.<br /><br /> It has been our pleasure to serve you.<br /><br /> If we can be of further assistance, please let us know at info@yapjoy.com.<br /><br />Best<br />YapJoy Team' % (
                           package.tokens),
                           'Successful Purchase!'
                           , 'Successful Purchase!')
                send_email('info@yapjoy.com',
                           'Congratulations on your recent purchase of %s tokens.<br /><br /> It has been our pleasure to serve you.<br /><br /> If we can be of further assistance, please let us know at info@yapjoy.com.<br /><br />Best<br />YapJoy Team' % (
                           package.tokens),
                           'Successful Purchase!'
                           , 'Successful Purchase!')
                return HttpResponseRedirect(reverse('vendors__storelisting'))
    return render(request, 'vendroid/demov2/vendors/listing/subscription.html',{
        'form':form,
        'package':package,
        # 'key':settings.STRIPE_PUBLISHABLE_KEY,
        'key':"pk_test_06mlzXo9xTcZCRy0XTkwYONA",
        'error_message':error_message,
    })

@login_required(login_url='/login/')

@login_required(login_url='/loginv3/')
@csrf_exempt
def dream_req(request, id):
    send_publishing = None
    send_publishing_error = None
    product = Product.objects.get(id=id)
    dreams = Dream.objects.select_related('product').filter(product_id=id,
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
    return render(request, 'vendroid/demov2/vendors/listing/dreams.html', context)






@login_required(login_url='/login/')
@csrf_exempt
def listing_answer(request, option_search_id, product_id, user_id):
    req_user = request.user
    try:
        ProductBids.objects.get(product_id=product_id, vendor_id=req_user.id)
        return HttpResponseRedirect(reverse('vendors__listing_bid', kwargs={'option_search_id':option_search_id,
                                                                          'product_id':product_id,
                                                                          'user_id':user_id}))
    except Exception as e:
        print 'Exception in answer: ',e
    user = User.objects.get(id=user_id)#request.user

    profile = req_user.userprofile
    print profile.subscribed
    gen_cat = optionsSearch.objects.get(name="General Questions")
    product_general_question = Product.objects.get(id=product_id)
    general_questions = ProductQuestion.objects.filter(Q(option_search__name='General Questions')).order_by("-id")
    general_answers = ProductAnswer.objects.select_related('product').filter(product_id=product_general_question.id, user=user_id,
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
    if 'total_items' in request.POST:
        if profile.amount > 0:
            total_items = request.POST.get('total_items')
            description = request.POST.get('description')
            bid = ProductBids.objects.create(product=product,
                                             description=description,
                                             vendor=req_user
                                             )
            profile.amount -= 1
            profile.save()
            vendor_view_object = VendorViewProduct.objects.get_or_create(vendor=req_user)[0]
            if not product_general_question.id in vendor_view_object.get_vendor_sent_list():
                if vendor_view_object.id_sent:
                    vendor_view_object.id_sent = "%s%s," % (vendor_view_object.id_sent, product_general_question.id)
                else:
                    vendor_view_object.id_sent = "%s," % (product_general_question.id)
                vendor_view_object.save()
            for x in range(int(total_items)+1):
                print 'value of x: ',x
                item = request.POST.get('item_id_'+str(x))
                price = request.POST.get('item_id_price_'+str(x))
                bid_item = BidItems.objects.create(product_bids=bid,
                                                   item=item,
                                                   price=price)
                bid.items.add(bid_item)
                print item, price, "---------"
                return HttpResponseRedirect(reverse('vendors__listing_bid', kwargs={'option_search_id': option_search_id,
                                                                                    'product_id': product_id,
                                                                                    'user_id': user_id}))

        # else:
            # error_subscription = "You donot have enough amount to "
    context = {
        'zipped_answers': zipped_answers,
        'zipped_answers_general': zipped_answers_general,
        'product': product,
        'profile': profile,
    }
    return render(request, 'vendroid/demov2/vendors/listing/answers.html', context)




@login_required(login_url='/login/')
@csrf_exempt
def listing_bid(request, option_search_id, product_id, user_id):
    user = request.user#User.objects.get(id=user_id)#request.user
    profile = user.userprofile

    # gen_cat = optionsSearch.objects.get(name="General Questions")
    # product_general_question = Product.objects.get_or_create(user=request.user, title="General Questions", category=gen_cat)[0]
    # general_questions = ProductQuestion.objects.filter(Q(option_search__name='General Questions')).order_by("-id")
    # general_answers = ProductAnswer.objects.select_related('product').filter(product_id=product_general_question.id, user=user,
    #                                                                  product_question__in=general_questions).order_by(
    #     "-product_question_id")
    # zipped_answers_general = zip(general_questions, general_answers)
    # questions = ProductQuestion.objects.filter(Q(option_search__id=option_search_id)).order_by("-id")
    #
    # answers = ProductAnswer.objects.select_related('product').filter(product__id=product_id, user=user, product_question__in=questions).order_by("-product_question_id")
    # product = Product.objects.get(id=product_id)
    # zipped_answers = zip(questions, answers)
    # print "zipped_answers", zipped_answers
    # if not answers:
    #     return HttpResponse('No answers available')
    # if 'total_items' in request.POST:
    #     total_items = request.POST.get('total_items')
    #     description = request.POST.get('description')
    #     bid = ProductBids.objects.create(product=product,
    #                                      description=description,
    #                                      )
    #     for x in range(int(total_items)+1):
    #         print 'value of x: ',x
    #         item = request.POST.get('item_id_'+str(x))
    #         price = request.POST.get('item_id_price_'+str(x))
    #         bid_item = BidItems.objects.create(product_bids=bid,
    #                                            item=item,
    #                                            price=price)
    #         bid.items.add(bid_item)
    #         print item, price, "---------"
    bid = ProductBids.objects.get(product_id=product_id, vendor_id=user.id)
    print 'bid is: ',bid
    context = {
        # 'zipped_answers': zipped_answers,
        # 'zipped_answers_general': zipped_answers_general,
        # 'product': product,
        # 'profile': profile,
        'bid': bid,
        'user': user,
    }
    return render(request, 'vendroid/demov2/vendors/listing/bids.html', context)


# @login_required(login_url='/login/')
@csrf_exempt
def StoreFrontView(request):
    initial = {
        # 'email': 'adeel@yapjoy.com',
        # 'first_name': 'Adeel',
        # 'last_name': 'K',
        # 'company_name': "YapJoy LLC",
        # 'phone': '111-222-333',
        # 'website_url': 'www.yapjoy.com',
        # 'business_location': 'CA',
        # 'state': 'CA',
        # 'zip': '112233',
    }
    form = StoreFront(initial=initial)
    if request.method == "POST":
        form = StoreFront(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            first_name = data['first_name']
            last_name = data['last_name']
            company_name = data['company_name']
            phone = data['phone']
            email = data['email']
            website_url = data['website_url']
            business_location = data['business_location']
            state = data['state']
            zip = data['zip']
            categories = data['categories']
            info = VendorRegistration.objects.create(first_name=first_name,
                                              last_name=last_name,
                                              email=email,
                                              company_name=company_name,
                                              phone=phone,
                                              website_url=website_url,
                                              business_location=business_location,
                                              categories=categories,
                                              state=state,
                                              zip=zip,
                                                     )
            info.code = id_generator()
            info.verification_code = id_generator(size=6)
            info.save()
            send_email(email, 'Email Verification Code', 'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.'%(info.verification_code), 'YapJoy Vendors Email Verification Code')
            print 'Submission Done'
            return HttpResponseRedirect(reverse("vendors__verify__code", kwargs={'code':info.code}))
        else:
            print form.errors
    context = {
        'form': form,
    }
    return render(request, 'vendroid/demov2/vendors/profile/vendorRegistration/profileForm_v2.html', context)


def StoreFrontv2(request):
    serializer = VendorSerializerRegister()


    return render(request, 'vendroid/demov2/vendors/profile/vendor_profileFormv2.html')
from django.contrib.auth import authenticate, logout, login as auth_login
from yapjoy_teamschat.models import EventTeam
@csrf_exempt
def invitation(request):
    #https://www.yajpjoy.com/family_share_link/{{ event.family_ref_code }}/
    #https://www.yapjoy.com/vendor_share_link/{{ event.family_ref_code }}/
    user_profile = UserProfile()
    if request.is_ajax():
        print "ajax"

        if request.method == 'GET' and request.GET.get('action') == 'email_next':

            email = request.GET.get('email')
            print "email: ", email
            usr = User.objects.filter(email=email)
            if usr:
                print "user exists", usr
                string = render_to_string('vendroid/demov2/profile/partials/_login_invite.html', {
                    'u': usr,
                })
                return HttpResponse(string)
            else:
                # send email user here with verification code
                user = User.objects.create(username=email, email=email)
                print "user: ", user
                verification_code = id_generator(size=6)
                user_profile = UserProfile.objects.get(user=user)

                user_profile.verification_code = verification_code
                user_profile.save()
                print "userprofile: ", user_profile
                send_email(email, 'Email Verification Code',
                           'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.' % (
                               verification_code), 'YapJoy Vendors Email Verification Code')

                string = render_to_string('vendroid/demov2/profile/partials/_verify_email.html', {
                    'u': user,
                })
                return HttpResponse(string)
        """Register Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'verify_email':
            code = request.POST.get('code')
            email = request.POST.get('email')
            print "code: ", code, email
            user_profile = UserProfile.objects.get(user__email=email)
            if user_profile.verification_code == code:
                print "code match"
                string = render_to_string('vendroid/demov2/profile/partials/_set_password.html', {
                    'u': user_profile,
                })

                return HttpResponse(string)
            else:
                return HttpResponse({'error':"Code didn't match"})
        if request.method == 'POST' and request.POST.get('action') == 'set_password':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "password: ", password, email
            user_profile = UserProfile.objects.get(user__email=email)
            user_profile.user.set_password(password)
            user_profile.save()
            print "code match"
            string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb.html', {
                'u': user_profile,
            })

            return HttpResponse(string)
        """Login Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'login_invite':
            print "login"
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "email: ", email, password
            # user_auth = authenticate(username=email, password=password)
            user_auth = User.objects.filter(username=email)
            print "user_auth: ", user_auth
            if user_auth is not None:
                user_profile = UserProfile.objects.get(user__email=email)
                string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb.html', {
                    'u': user_profile,
                })

                return HttpResponse(string)
        if request.method == 'POST'  and request.POST.get('action') == 'edit_profile':
            print "edit profile POST"
            full_name = request.POST.get('full_name')
            role = request.POST.get('role')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            print "profile: ", email, role, full_name, phone
            user_profile = UserProfile.objects.get(user__email=email)
            user_profile.user.first_name = full_name.split(' ')[0]
            user_profile.user.last_name = full_name.split(' ')[1]
            user_profile.user.email = email
            user_profile.phone = phone
            user_profile.user.save()
            user_profile.profession = role
            user_profile.save()
            string = render_to_string('vendroid/demov2/profile/partials/_edit_profile.html', {
                'u' : user_profile,
            })
            return HttpResponse(string)


    else:
        print "not ajax"

    return render(request, 'vendroid/demov2/profile/invitation.html')


from django.contrib import auth
@csrf_exempt
def invitationfamily(request, code):
    user_profile = UserProfile()
    event = EventTeam.objects.get(family_ref_code=code)
    print "evvent: ", event
    if request.is_ajax():
        print "ajax"

        if request.method == 'GET' and request.GET.get('action') == 'email_next':

            email = request.GET.get('email')
            print "email: ", email
            usr = User.objects.filter(email=email)
            if usr:
                print "user exists", usr, event
                string = render_to_string('vendroid/demov2/profile/partials/_login_invite.html', {
                    'u': usr,
                    'event': event
                })
                return HttpResponse(string)
            else:
                # send email user here with verification code
                user = User.objects.create(username=email, email=email)
                print "user: ", user
                verification_code = id_generator(size=6)
                user_profile = UserProfile.objects.get(user=user)
                vendor = VendorRegistration.objects.create(user=user, email=email, code=id_generator())
                vendor.verification_code = verification_code
                vendor.save()

                # user_profile.verification_code = verification_code
                # user_profile.save()
                print "userprofile: ", user_profile
                send_email(email, 'Email Verification Code',
                           'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.' % (
                               verification_code), 'YapJoy Vendors Email Verification Code')

                string = render_to_string('vendroid/demov2/profile/partials/_verify_email.html', {
                    'u': user,
                    'event': event
                })
                return HttpResponse(string)
        """Register Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'verify_email':
            code = request.POST.get('code')
            email = request.POST.get('email')
            print "code: ", code, email
            user_profile = UserProfile.objects.get(user__email=email)
            vendor = VendorRegistration.objects.get(user__email=email)
            if vendor.verification_code == code:
                print "code match"
                event.friends.add(vendor.user)
                event.save()
                string = render_to_string('vendroid/demov2/profile/partials/_set_password.html', {
                    'u': user_profile,
                    'event': event
                })

                return HttpResponse(string)
            else:
                return HttpResponse({'error':"Code didn't match"})
        if request.method == 'POST' and request.POST.get('action') == 'set_password':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "password: ", password, email
            user_profile = UserProfile.objects.get(user__email=email)
            user_profile.user.set_password(password)

            user_profile.user.save()
            user_profile.type = UserProfile.UNKNOWN

            user_profile.save()
            user_auth = auth.authenticate(username=email, password=password)
            print "flow: ", user_auth
            sub = None
            if user_auth.is_active:
                user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user_auth)
                print 'auth flow'

                event.friends.add(user_auth)
                event.save()

            print "code match"

            string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb.html', {
                'u': user_profile,
                'event': event
            })

            return HttpResponse(string)
        """Login Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'login_invite':
            print "login"
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "email: ", email, password
            user_auth = auth.authenticate(username=email, password=password)
            print user_auth
            sub = None
            if user_auth.is_active:
                # try:
                #     sub = SubscriptionCode.objects.get(user=user_auth)
                # except:
                #     sub = SubscriptionCode.objects.create(user=user_auth, code=id_generator())
                # profile = user_auth.userprofile
                # if not sub.is_subscribed and (profile.type == UserProfile.BRIDE or profile.type == UserProfile.GROOM):
                #     return HttpResponseRedirect('/subscribe/%s/'%(sub.code))


                user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user_auth)
                event.friends.add(user_auth)
                event.save()
                print 'auth'

            user_auth = User.objects.filter(username=email)
            print "user_auth: ", user_auth
            if user_auth is not None:
                user_profile = UserProfile.objects.get(user__email=email)
                user_profile.type = UserProfile.UNKNOWN
                user_profile.save()

                # event.friends.add(user_auth)
                # event.save()

                string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb.html', {
                    'u': user_profile,
                    'event': event
                })

                return HttpResponse(string)
        if request.method == 'POST'  and request.POST.get('action') == 'edit_profile':
            print "edit profile POST"
            full_name = request.POST.get('full_name')
            role = request.POST.get('role')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            print "profile: ", email, role, full_name, phone
            user_profile = UserProfile.objects.get(user__email=email)
            vendor = VendorRegistration.objects.get(user__email=email)

            if ' ' in full_name:
                vendor.first_name = full_name.split(' ')[0]
                vendor.last_name = full_name.split(' ')[1]
            else:
                vendor.first_name = full_name

            # vendor.first_name = full_name.split(' ')[0]
            # vendor.last_name = full_name.split(' ')[1]
            vendor.phone = phone
            vendor.profession = role
            vendor.save()

            if ' ' in full_name:
                user_profile.user.first_name = full_name.split(' ')[0]
                user_profile.user.last_name = full_name.split(' ')[1]
            else:
                user_profile.user.first_name = full_name

            # user_profile.user.first_name = full_name.split(' ')[0]
            # user_profile.user.last_name = full_name.split(' ')[1]
            user_profile.user.email = email
            # user_profile.profession = role
            user_profile.user.save()
            user_profile.phone = phone
            user_profile.profession = role
            user_profile.save()
            # string = render_to_string('vendroid/demov2/profile/partials/_edit_profile.html', {
            #     'u' : user_profile,
            #     'event': event
            # })
            # return HttpResponse(string)
            return render(request, 'vendroid/demov2/profile/bg_page.html', {'u': user_profile, 'event': event})


    else:
        print "not ajax"

    return render(request, 'vendroid/demov2/profile/invitation.html', {'event':event})

@csrf_exempt
def invitationvendor(request, code):
    user_profile = UserProfile()
    event = EventTeam.objects.get(vendor_ref_code=code)
    print "evvent: ", event
    if request.is_ajax():
        print "ajax"

        if request.method == 'GET' and request.GET.get('action') == 'email_next':

            email = request.GET.get('email')
            print "email: ", email
            usr = User.objects.filter(email=email)
            if usr:
                print "user exists", usr, event
                string = render_to_string('vendroid/demov2/profile/partials/_login_invite_vendor.html', {
                    'u': usr,
                    'event': event
                })
                return HttpResponse(string)
            else:
                # send email user here with verification code
                user = User.objects.create(username=email, email=email)
                print "user: ", user
                verification_code = id_generator(size=6)

                user_profile = UserProfile.objects.get(user=user)
                vendor = VendorRegistration.objects.create(user=user, email=email, code=id_generator())
                vendor.verification_code = verification_code
                vendor.save()
                # user_profile.verification_code = verification_code
                # user_profile.save()
                print "userprofile: ", user_profile
                send_email(email, 'Email Verification Code',
                           'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.' % (
                               verification_code), 'YapJoy Vendors Email Verification Code')

                string = render_to_string('vendroid/demov2/profile/partials/_verify_email_vendor.html', {
                    'u': user,
                    'event': event
                })
                return HttpResponse(string)
        """Register Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'verify_email':
            code = request.POST.get('code')
            email = request.POST.get('email')
            print "code: ", code, email
            user_profile = UserProfile.objects.get(user__email=email)
            vendor = VendorRegistration.objects.get(user__email=email)
            if vendor.verification_code == code:
                print "code match"
                event.friends.add(vendor.user)
                event.save()
                string = render_to_string('vendroid/demov2/profile/partials/_set_password_vendor.html', {
                    'u': user_profile,
                    'event': event
                })

                return HttpResponse(string)
            else:
                return HttpResponse({'error': "Code didn't match"})
        if request.method == 'POST' and request.POST.get('action') == 'set_password':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "password: ", password, email
            user_profile = UserProfile.objects.get(user__email=email)
            user_profile.user.set_password(password)
            user_profile.user.save()
            user_profile.type = UserProfile.PROFESSIONAL

            user_profile.save()
            user_auth = auth.authenticate(username=email, password=password)
            print "flow: ", user_auth
            sub = None
            if user_auth.is_active:
                user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user_auth)
                print 'auth flow'

                event.friends.add(user_auth)
                event.save()

            print "code match"
            string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb_vendor.html', {
                'u': user_profile,
                'event': event
            })

            return HttpResponse(string)
        """Login Flow"""
        if request.method == 'POST' and request.POST.get('action') == 'login_invite':
            print "login"
            email = request.POST.get('email')
            password = request.POST.get('password')
            print "email: ", email, password
            user_auth = auth.authenticate(username=email, password=password)
            print user_auth
            sub = None
            if user_auth.is_active:

                user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user_auth)
                print 'auth'

                event.friends.add(user_auth)
                event.save()

            user_auth = User.objects.filter(username=email)

            print "user_auth: ", user_auth
            if user_auth is not None:
                user_profile = UserProfile.objects.get(user__email=email)
                user_profile.type = UserProfile.PROFESSIONAL
                user_profile.save()
                string = render_to_string('vendroid/demov2/profile/partials/_loggedinWeb_vendor.html', {
                    'u': user_profile,
                    'event': event
                })

                return HttpResponse(string)
        if request.method == 'POST' and request.POST.get('action') == 'edit_profile':
            print "edit profile POST"
            full_name = request.POST.get('full_name')
            role = request.POST.get('role')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            print "profile: ", email, role, full_name, phone
            user_profile = UserProfile.objects.get(user__email=email)

            vendor = VendorRegistration.objects.get(user__email=email)
            if ' ' in full_name:
                vendor.first_name = full_name.split(' ')[0]
                vendor.last_name = full_name.split(' ')[1]
            else:
                vendor.first_name = full_name
            vendor.phone = phone
            vendor.profession = role
            vendor.save()

            if ' ' in full_name:
                user_profile.user.first_name = full_name.split(' ')[0]
                user_profile.user.last_name = full_name.split(' ')[1]
            else:
                user_profile.user.first_name = full_name

            # user_profile.user.first_name = full_name.split(' ')[0]
            # user_profile.user.last_name = full_name.split(' ')[1]
            user_profile.user.email = email


            user_profile.user.save()
            # user_profile.profession = role
            # user_profile.save()
            user_profile.phone = phone
            user_profile.profession = role
            user_profile.save()
            # string = render_to_string('vendroid/demov2/profile/partials/_edit_profile.html', {
            #     'u': user_profile,
            #     'event': event
            # })
            # return HttpResponse(string)
            return render(request, 'vendroid/demov2/profile/bg_page.html', {'u':user_profile, 'event':event})


    else:
        print "not ajax"

    return render(request, 'vendroid/demov2/profile/invitation_vendors.html', {'event': event})


def bg_page(request):
    return render(request, 'vendroid/demov2/profile/bg_page.html')

# @app.route('/sign_s3/')
import os
import boto3
import json
def sign_s3(request):
    print "sign_s3"
    S3_BUCKET = 'yapjoy-static'
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')

    ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
    SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY

    # images_allowed = ['image/jpeg', 'image/png']
    #
    # if file_type not in images_allowed:
    #     data = json.dumps({'error': 'Invalid file type (%s).' % file_type})
    #     print "Data", data
    #     return HttpResponse(data, content_type="application/json", status=200)
    file_name = 'media/vendorsVideos/%s_%s' %(datetime.now(),file_name)
    file_name = file_name.replace(' ', '')
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
    )

    content = json.dumps({'data': presigned_post, 'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
                          })

    print "content", content
    return HttpResponse(content, content_type="application/json")

@login_required(login_url='/login/')
@csrf_exempt
def StoreFrontEdit(request):
    user = request.user
    up = user.userprofile
    try:
        company = Company.objects.get(userprofile=up)
    except:
        Company.objects.create(userprofile=up)
    success = ""
    initial = {
        # 'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'company_name': up.profession,
        'phone': up.phone,
        'profession': up.profession,
        # 'website_url': up.website_url,
        # 'business_location': up.city,
        # 'state': up.state,
        # 'zip': up.zip,
        # 'categories': up.ca,
    }
    form = StoreFrontEditForm(initial=initial)
    if request.method == "POST":
        form = StoreFrontEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            first_name = data['first_name']
            last_name = data['last_name']
            profession = data['profession']
            phone = data['phone']
            # email = data['email']
            # website_url = data['website_url']
            # business_location = data['business_location']
            # state = data['state']
            # zip = data['zip']
            # categories = data['categories']
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # company = up.userprofile_company
            # company.name = company_name
            # company.save()
            # up.zip = zip
            # up.state = state
            # up.city = business_location
            up.phone = phone
            up.profession = profession
            # up.website_url = website_url
            up.save()
            success = "Information saved successfully."
            return HttpResponseRedirect(reverse('vendors__profile'))
            print success
        else:
            print form.errors
            # info.code = id_generator()
            # info.verification_code = id_generator(size=6)
            # info.save()
            # send_email(email, 'Email Verification Code', 'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.'%(info.verification_code), 'YapJoy Vendors Email Verification Code')
            # print 'Submission Done'
            # return HttpResponseRedirect(reverse("vendors__verify__code", kwargs={'code':info.code}))
    context = {
        'form': form,
        'vendor': user,
        'success': success,
    }
    return render(request, 'vendroid/demov2/vendors/profile/profileEdit.html', context)


from .functions import get_or_create_user
# @login_required(login_url='/login/')
@csrf_exempt
def verify_email(request, code):
    obj = get_object_or_404(VendorRegistration, code=code)
    form = VerifyEmailCode()
    error = None
    if request.method == "POST":
        form = VerifyEmailCode(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            code = data['code']
            if obj.verification_code == code:
                print 'verified'
                user = get_or_create_user(obj.email)
                if user:
                    obj.user = user
                    obj.status = VendorRegistration.VERIFIED
                    obj.save()
                    return HttpResponseRedirect(reverse('vendors__setup_password',kwargs={'code':obj.code}))
            error = "Code is not valid."
    context = {
        'error':error,
        'form':form,
    }
    return render(request, 'vendroid/demov2/vendors/profile/verify_email.html', context)

@csrf_exempt
def SetupPasswordView(request, code):
    obj = get_object_or_404(VendorRegistration, code=code, status=VendorRegistration.VERIFIED)
    form = SetupPasswordForm()
    error = None
    if request.method == "POST":
        print request.POST
        form = SetupPasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            password = data['password']
            print password
            user = obj.user
            user.set_password(password)
            user.save()
            up = user.userprofile
            company = None
            try:
                company = Company.objects.get(userprofile=up)
            except:
                company = Company.objects.create(userprofile=up)
            company.name = obj.company_name
            company.save()
            up.city = obj.business_location
            up.state = obj.state
            up.save()
            send_email(user.email, 'Your email has been verified.<br /><br />Please login at<br /><br />www.yapjoy.com/login/professional/',
                       'Welcome to YapJoy!'
                      , 'Welcome to YapJoy!')
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return HttpResponseRedirect(reverse('vendors__profile'))
    context = {
        'error':error,
        'form':form,
    }
    print form
    return render(request, 'vendroid/demov2/vendors/profile/setup_password.html', context)


@login_required(login_url='/login/')
@staff_member_required
@csrf_exempt
def profile_admin(request):
    user_list = VendorRegistration.objects.all().values_list('user_id', flat=True)
    profiles = UserProfile.objects.select_related('user').filter(Q(is_review_request=True)|Q(user__in=user_list))
    if 'vendor_id' in request.POST:
        prof_approve = UserProfile.objects.get(id=request.POST.get('vendor_id'))
        prof_approve.is_approved = True
        prof_approve.save()
        return HttpResponseRedirect('')

    return render(request, 'vendroid/demov2/admin/profile_list.html',{
        'profiles':profiles,
    })

@login_required(login_url='/login/professional/')
@csrf_exempt
def profile(request):
    #Numbers of product intended to display
    # in the next click of lazy load
    user = request.user
    up = user.userprofile
    # try:
    #     up = UserProfile.objects.get(user__id=id)
    #     if up.type != UserProfile.PROFESSIONAL:
    #         return HttpResponse("You have to be a wedding professional")
    # except Exception as e:
    #     return HttpResponse("The url is incorrect.")
    profile__image__form = VendorProfileImageForm()
    videoForm = vendorVideoForm()
    if request.method == "POST":
        print request.POST
        print request.FILES
        if "videoUrl" in request.POST:
            videoUrl = request.POST.get('videoUrl')
            up.video_url = videoUrl
            up.save()

            context = {
                'videoUrl': videoUrl
            }
            return render(request, 'vendroid/demov2/vendors/profile/_partial_video.html', context)

        elif "description" in request.POST:
            description = request.POST.get('description')
            try:
                comp = Company.objects.get(userprofile=up)
                comp.description = description
                comp.save()
            except:
                Company.objects.create(userprofile=up,
                                       description=description)
            description = None
            try:
                comp = Company.objects.get(userprofile=up)
                company_name = comp.name
                description = comp.description
            except:
                company_name = ""
                description = ""
            # return HttpResponse("successs")
            return render(request, 'vendroid/demov2/vendors/profile/_partial_about_desc.html', {
                'up':up,
                'description':description,
            })

        elif "facebook_url" in request.POST:
            facebook_url = request.POST.get('facebook_url')
            twitter_url = request.POST.get('twitter_url')
            pinterest_url = request.POST.get('pinterest_url')
            youtube_url = request.POST.get('youtube_url')
            instagram_url = request.POST.get('instagram_url')
            yelp_url = request.POST.get('yelp_url')

            up.facebook_url = facebook_url
            up.twitter_url = twitter_url
            up.pinterest_url = pinterest_url
            up.youtube_url = youtube_url
            up.instagram_url = instagram_url
            up.yelp_url = yelp_url
            up.save()
            # description = None
            # try:
            #     comp = Company.objects.get(userprofile=up)
            #     company_name = comp.name
            #     description = comp.description
            # except:
            #     company_name = ""
            #     description = ""

            # return HttpResponse("successs")
            return render(request, 'vendroid/demov2/vendors/profilev2/_social_media_icons.html', {
                'up': up,
                # 'description': description,
            })

        elif "packageID" in request.POST:
            packageID = request.POST.get('packageID')
            price = request.POST.get('packageprice')
            title = request.POST.get('packagetitle')
            description = request.POST.get('packagedescription')

            print packageID
            if str(packageID) == "0":
                Package.objects.create(user=up.user,
                                       price=price,
                                       title=title,
                                       description=description)
                packages = Package.objects.filter(user__userprofile=up).order_by("-created_at")
                context = {
                    'packages': packages
                }
                return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPackages.html', context)
            else:
                try:
                    pkg = Package.objects.get(id=packageID)
                    pkg.price = price
                    pkg.title = title
                    pkg.description = description
                    pkg.save()

                    packages = Package.objects.filter(user__userprofile=up).order_by("-created_at")
                    context = {
                        'packages': packages
                    }
                    return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPackages.html', context)

                except Exception as e:
                    print "get package error", e
                    return Http404

        elif "deletePackageID" in request.POST:
            packageID = request.POST.get('deletePackageID')
            print packageID

            try:
                pkg = Package.objects.get(id=packageID)
                pkg.delete()

                packages = Package.objects.filter(user__userprofile=up).order_by("-created_at")
                context = {
                    'packages': packages
                }
                return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPackages.html', context)

            except Exception as e:
                print "get package error", e
                return Http404

        elif "YelpName" in request.POST:
            YelpName = request.POST.get('YelpName')
            YelpZip = request.POST.get('YelpZip')

            try:
                up.yelp_name = YelpName
                up.yelp_location_zip = YelpZip
                up.save()

                try:
                    y_imageUrl = up.get_yelp_profile_image()
                except:
                    y_imageUrl = ""

                try:
                    y_descp = up.get_yelp_description()
                except:
                    y_descp = ""

                context = {
                    'yelp_description': y_descp,
                    'yelp_image': y_imageUrl,
                    'up': up,
                }
                print context
                return render(request, 'vendroid/demov2/vendors/profile/_partial_yelp.html', context)

            except Exception as e:
                print "get package error", e
                return Http404

        elif "deleteAlbumID" in request.POST:
            deleteAlbumID = request.POST.get('deleteAlbumID')
            if deleteAlbumID > 0:
                try:
                    album = VendorAlbum.objects.get(id=deleteAlbumID)
                    album.delete()

                    albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
                    try:
                        photos = VendorImage.objects.select_related('album').filter(album__in=albums).order_by("-created_at")
                    except:
                        photos = [[]*len(albums)]
                    zipped_images = zip(albums, photos)
                    context = {
                        'zipped_images': zipped_images,
                    }
                    return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPhotos.html', context)
                except:
                    return Http404

            else:
                Http404
        elif "change_profile_picture" in request.POST:
            print 'inside change_profile_picture'

            profile__image__form = VendorProfileImageForm(request.POST, request.FILES)
            if profile__image__form.is_valid():
                print 'updating change_profile_picture'
                data = profile__image__form.cleaned_data
                up.image = data['image']
                up.save()
                # print up.image.url
                return HttpResponse(up.image.url)
        elif "deletePhotoID" in request.POST:
            deletePhotoID = request.POST.get('deletePhotoID')
            try:
                image = VendorImage.objects.get(id=deletePhotoID)
                image.delete()

                albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
                try:
                    photos = VendorImage.objects.select_related('album').filter(album__in=albums).order_by(
                        "-created_at")
                except:
                    photos = [[] * len(albums)]
                zipped_images = zip(albums, photos)
                context = {
                    'zipped_images': zipped_images,
                }
                return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPhotos.html', context)
            except:
                return Http404

        elif "changeAlbumTitle" in request.POST:
            changeAlbumTitleID = request.POST.get('changeAlbumTitleID')
            title = request.POST.get('title')

            if changeAlbumTitleID > 0:
                try:
                    album = VendorAlbum.objects.get(id=changeAlbumTitleID)
                    album.title = title
                    album.save()

                    return HttpResponse("success")
                except:
                    return Http404

            else:
                try:
                    VendorAlbum.objects.create(user=user, title=title)

                    albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
                    try:
                        photos = VendorImage.objects.select_related('album').filter(album__in=albums).order_by(
                            "-created_at")
                    except:
                        photos = [[] * len(albums)]
                    zipped_images = zip(albums, photos)
                    context = {
                        'zipped_images': zipped_images,
                    }
                    return render(request, 'vendroid/demov2/vendors/profile/_partial_hasPhotos.html', context)
                except:
                    return Http404
        elif "video_new_url" in request.POST:
            video_new_url = request.POST.get('video_new_url')
            up.video_url = video_new_url
            up.save()
            context = {
                'up': up
            }
            return render(request, 'vendroid/demov2/vendors/profile/_partial_video.html', context)
        elif "uploadVideo" in request.POST:
            videoForm = vendorVideoForm(request.POST, request.FILES)
            if videoForm.is_valid():
                data = videoForm.cleaned_data
                video = data['video']
                up.video = video
                up.save()
                context = {
                    'videoUrl':up.video
                }
                return render(request, 'vendroid/demov2/vendors/profile/_partial_video.html', context)
        elif "apply_now_profile" in request.POST:
            print 'in apply_now_profile'
            if not up.is_review_request:
                up.is_review_request = True
                up.review_request_date = datetime.now()
                up.save()
                return render(request, 'vendroid/demov2/vendors/profile/_partial_submission.html')
            else:
                return HttpResponse('Already submitted')
        elif "AlbumPictureID" in request.POST:
            AlbumPictureID = request.POST.get('AlbumPictureID')
            VendorImage.objects.get(id=AlbumPictureID, album__user=user).delete()
            photos = VendorImage.objects.select_related('album').filter(album__user=user).order_by("-created_at")
            # if photos and albums:
            #     zipped_images = zip(albums, photos)
            # zipped_images = zip(albums, photos)
            print 'done removing'
            context = {
                # 'zipped_images': zipped_images,
                'photos': photos,
            }
            return render(request, 'vendroid/demov2/vendors/profile/_partial_images.html', context)
        elif "set_my_location_val" in request.POST:
            set_my_location_val = request.POST.get('set_my_location_val')
            up.street = set_my_location_val
            up.save()
            print set_my_location_val
            return HttpResponse('Done')
            return render(request, "vendroid/demov2/vendors/profilev2/_location.html")
        # elif request.method == "POST":
        #     """
        #     TODO: Fix me of image loading
        #     """
        #     print 'uploading file for picture album here'
        #     formData = vendorImageForm(request.POST, request.FILES)
        #     if formData.is_valid():
        #         print 'form is valid'
        #         image = formData.cleaned_data['image']
        #         print 'image is taken'
        #         if VendorAlbum.objects.filter(user=request.user).count() == 0:
        #             VendorAlbum.objects.create(user=request.user)
        #         vendor__album = VendorAlbum.objects.filter(user=request.user)[0]
        #         print vendor__album
        #         print 'image album is found'
        #         VendorImage.objects.create(album=vendor__album, image=image)
        #         print 'image is saved'
        #
        #         # albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
        #         photos = VendorImage.objects.select_related('album').filter(album__user=user).order_by("-created_at")
        #         # if photos and albums:
        #         #     zipped_images = zip(albums, photos)
        #         # zipped_images = zip(albums, photos)
        #         print 'done uploading'
        #         context = {
        #             # 'zipped_images': zipped_images,
        #             'photos': photos,
        #         }
        #         return render(request, 'vendroid/demov2/vendors/profile/_partial_images.html', context)
        #     else:
        #         print 'form was not valid'
        #         print formData.errors


    #First time loading
    # try:
    #     up = UserProfile.objects.get(user__id=id)
    #     if up.type != UserProfile.PROFESSIONAL:
    #        return HttpResponse("You have to be a wedding professional")
    # except Exception as e:
    #     return HttpResponse("The url is incorrect.")

    try:
        comp = Company.objects.get(userprofile=up)
        company_name = comp.name
        description = comp.description
    except:
        company_name = ""
        description = ""

    try:
        packages = Package.objects.filter(user_id=user.id).order_by("-created_at")
    except:
        packages = []

    # Yelp's
    try:
        y_imageUrl = up.get_yelp_profile_image()
    except:
        y_imageUrl = ""

    try:
        y_descp = up.get_yelp_description()
    except:
        y_descp = ""

    zipped_images = []
    photos = []
    # Images
    # try:
    #     albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
    #     try:
    #         photos = VendorImage.objects.filter(album__in=albums).order_by("-created_at")
    #     except:
    #         photos = []#[[] * len(albums)]
    #     # if photos and albums:
    #     #     zipped_images = zip(albums, photos)
    # except:
    #     zipped_images = []
    print "Zipped", zipped_images
    initial_yelp = {}
    # if up.yelp_name and up.yelp_location_zip:
    #     initial_yelp = {
    #         'yelp_name': up.yelp_name,
    #         'yelp_location_zip': up.yelp_location_zip,
    #     }
    yelp_form = yelpForm(initial=initial_yelp)
    profile_image_form = None
    video_upload_s3_form = S3DirectUploadForm()
    context = {
        'up': up,
        'videoUrl': up.video,
        'description': description,
        'company_name': company_name,
        'packages': packages,
        'yelp_form': yelp_form,
        'yelp_description': y_descp,
        'yelp_image': y_imageUrl,
        'zipped_images': zipped_images,
        'photos': photos,
        'videoForm': videoForm,
        'profile': up,
        'profile__image__form': profile__image__form,
        'video_upload_s3_form': video_upload_s3_form,
    }
    # return render(request, 'vendroid/demov2/vendors/profile/profile.html', context)
    return render(request, 'vendroid/demov2/vendors/profile/yapjoy_storefront/storefront_builder.html', context)



# @login_required(login_url='/login/professional/')
# @csrf_exempt
def profileView(request, id):
    #Numbers of product intended to display
    # in the next click of lazy load

    up = get_object_or_404(UserProfile, id=id)
    # user = up.user

    try:
        comp = Company.objects.get(userprofile=up)
        company_name = comp.name
        description = comp.description
    except:
        company_name = ""
        description = ""


    context = {
        'up': up,
        'videoUrl': up.video,
        'description': description,
        'company_name': company_name,
        'profile': up,
    }
    # return render(request, 'vendroid/demov2/vendors/profile/profile.html', context)
    return render(request, 'vendroid/demov2/vendors/profile/yapjoy_storefront/storefront_builder_view.html', context)



@login_required(login_url='/login/')
@csrf_exempt
@staff_member_required
def profile_admin_view(request, profile_id):

    up = get_object_or_404(UserProfile, id=profile_id)
    user = up.user
    profile__image__form = VendorProfileImageForm()
    videoForm = vendorVideoForm()

    try:
        comp = Company.objects.get(userprofile=up)
        company_name = comp.name
        description = comp.description
    except:
        company_name = ""
        description = ""

    try:
        packages = Package.objects.filter(user_id=user.id).order_by("-created_at")
    except:
        packages = []

    # Yelp's
    try:
        y_imageUrl = up.get_yelp_profile_image()
    except:
        y_imageUrl = ""

    try:
        y_descp = up.get_yelp_description()
    except:
        y_descp = ""

    zipped_images = []
    photos = []
    # Images
    try:
        albums = VendorAlbum.objects.filter(user=user).order_by("-created_at")
        try:
            photos = VendorImage.objects.filter(album__in=albums).order_by("-created_at")
        except:
            photos = []#[[] * len(albums)]
        # if photos and albums:
        #     zipped_images = zip(albums, photos)
    except:
        zipped_images = []
    print "Zipped", zipped_images
    initial_yelp = {}
    if up.yelp_name and up.yelp_location_zip:
        initial_yelp = {
            'yelp_name': up.yelp_name,
            'yelp_location_zip': up.yelp_location_zip,
        }
    yelp_form = yelpForm(initial=initial_yelp)
    profile_image_form = None
    context = {
        'up': up,
        'videoUrl': up.video,
        'description': description,
        'company_name': company_name,
        'packages': packages,
        'yelp_form': yelp_form,
        'yelp_description': y_descp,
        'yelp_image': y_imageUrl,
        'zipped_images': zipped_images,
        'photos': photos,
        'videoForm': videoForm,
        'profile__image__form': profile__image__form,
    }
    return render(request, 'vendroid/demov2/vendors/profile/profile.html', context)


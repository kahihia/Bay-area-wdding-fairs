from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from yapjoy_registration.models import *
from django.db.models import Sum

# @login_required(login_url='/login/')
@csrf_exempt
def shortlist(request, category, product_id):
    # user = request.user
    # profile = user.userprofile
    N = 5
    # print user.id
    # if profile.type != UserProfile.PROFESSIONAL:

    # recommendations------TODO: need improved later
    # service = optionsSearch.objects.get(name=name)
    # print "category", category
    # try:
    #     shortlists = Shortlist.objects.filter(user=user, category__icontains=category)
    # except:
    #     shortlists = {}

    suggestions = UserProfile.objects.select_related('user').filter(looking_for__icontains=category,
                                             type=UserProfile.PROFESSIONAL).exclude(yelp_location_zip__isnull=True).exclude(yelp_name__isnull=True).order_by('-last_seen')[:N]
    # print "recommend", suggestions

    # if request.method == 'POST':
    #     if 'addID' in request.POST:
    #         addid = request.POST.get('addID')
    #         print "addID", addid
    #         try:
    #             number = Shortlist.objects.filter(vendor__id=addid, user=user).count()
    #         except:
    #             number = 0
    #
    #         if number == 0:
    #             Shortlist.objects.create(
    #                                     # user_id=user.id,
    #                                      vendor_id=addid, category=category)
    #             print "created"
    #             shortlist = Shortlist.objects.filter(
    #                 # user=user,
    #                 category=category)
    #
    #             context = {
    #                 'shortlists': shortlist,
    #             }
    #             print "after adding shortlist", shortlist
    #
    #             return render(request, 'vendroid/demov2/shortlist/_partial_shortlist.html', context)

        # elif 'removeID' in request.POST:
        #     print "removing"
        #     removeID = request.POST.get('removeID')
        #     print "remove ID", removeID
        #
        #     s = Shortlist.objects.get(id=removeID)
        #     print "s", s
        #     s.delete()
        #     shortlist = Shortlist.objects.filter(user=user, category=category)
        #     # suggestions = UserProfile.objects.filter(looking_for__icontains=category, type=UserProfile.PROFESSIONAL).exclude(id__in=shortlists).order_by('-last_seen')[:N]
        #
        #     context = {
        #         # 'suggestions': suggestions,
        #         'shortlists': shortlist,
        #     }
        #     print "after removing shortlist", suggestions
        #
        #     # return render(request, 'vendroid/shortlist/_partial_suggestions.html', context)
        #     return render(request, 'vendroid/demov2/shortlist/_partial_shortlist.html', context)

    # print "shortlists", shortlists

    context = {
        # 'shortlists': shortlists,
        'suggestions': suggestions,
        'category': category,
        'product_id': product_id,
    }
    return render(request, 'vendroid/demov2/shortlist/shortlist.html', context)

    # else:
    #     return HttpResponse('This interface is for Brides and Grooms only, Your Profile type is Professional.')


@login_required(login_url='/login/')
@csrf_exempt
def shortlist_req(request, category, product_id):
    # user = request.user
    # profile = user.userprofile
    N = 5
    # print user.id
    # if profile.type != UserProfile.PROFESSIONAL:

    # recommendations------TODO: need improved later
    # service = optionsSearch.objects.get(name=name)
    # print "category", category
    # try:
    #     shortlists = Shortlist.objects.filter(user=user, category__icontains=category)
    # except:
    #     shortlists = {}

    # suggestions = UserProfile.objects.select_related('user').filter(looking_for__icontains=category,
    #                                          type=UserProfile.PROFESSIONAL).exclude(yelp_location_zip__isnull=True).exclude(yelp_name__isnull=True).order_by('-last_seen')[:N]
    # print "recommend", suggestions

    # if request.method == 'POST':
    #     if 'addID' in request.POST:
    #         addid = request.POST.get('addID')
    #         print "addID", addid
    #         try:
    #             number = Shortlist.objects.filter(vendor__id=addid, user=user).count()
    #         except:
    #             number = 0
    #
    #         if number == 0:
    #             Shortlist.objects.create(
    #                                     # user_id=user.id,
    #                                      vendor_id=addid, category=category)
    #             print "created"
    #             shortlist = Shortlist.objects.filter(
    #                 # user=user,
    #                 category=category)
    #
    #             context = {
    #                 'shortlists': shortlist,
    #             }
    #             print "after adding shortlist", shortlist
    #
    #             return render(request, 'vendroid/demov2/shortlist/_partial_shortlist.html', context)

        # elif 'removeID' in request.POST:
        #     print "removing"
        #     removeID = request.POST.get('removeID')
        #     print "remove ID", removeID
        #
        #     s = Shortlist.objects.get(id=removeID)
        #     print "s", s
        #     s.delete()
        #     shortlist = Shortlist.objects.filter(user=user, category=category)
        #     # suggestions = UserProfile.objects.filter(looking_for__icontains=category, type=UserProfile.PROFESSIONAL).exclude(id__in=shortlists).order_by('-last_seen')[:N]
        #
        #     context = {
        #         # 'suggestions': suggestions,
        #         'shortlists': shortlist,
        #     }
        #     print "after removing shortlist", suggestions
        #
        #     # return render(request, 'vendroid/shortlist/_partial_suggestions.html', context)
        #     return render(request, 'vendroid/demov2/shortlist/_partial_shortlist.html', context)

    # print "shortlists", shortlists

    context = {
        # 'shortlists': shortlists,
        # 'suggestions': suggestions,
        # 'category': category,
        # 'product_id': product_id,
    }
    return render(request, 'vendroid/demov2/shortlist/shortlistv2.html', context)

    # else:
    #     return HttpResponse('This interface is for Brides and Grooms only, Your Profile type is Professional.')
from django.shortcuts import render, Http404
from yapjoy_registration.models import UserProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
@login_required(login_url='/login/')
def directory(request):
    user = request.user
    profile = user.userprofile
    # if not profile.type == UserProfile.PROFESSIONAL:
    #     raise Http404
    userprofiles = None
    if 'name' in request.GET:
        name = request.GET.get('name')
        userprofiles = UserProfile.objects.filter(Q(user__username__icontains=name)|Q(user__email__icontains=name)|Q(user__first_name__icontains=name)|Q(user__last_name__icontains=name)).select_related('user').order_by('-subscribed')
    elif 'bride' in request.GET:
        userprofiles = UserProfile.objects.filter(type=UserProfile.BRIDE).exclude(user=user).select_related('user').order_by('-subscribed')
    elif 'groom' in request.GET:
        userprofiles = UserProfile.objects.filter(type=UserProfile.GROOM).exclude(user=user).select_related('user').order_by('-subscribed')
    elif 'weddingprofessional' in request.GET:
        userprofiles = UserProfile.objects.select_related('userprofile_company').filter(type=UserProfile.PROFESSIONAL).exclude(user=user).select_related('user').order_by('-subscribed')
    else:
        userprofiles = UserProfile.objects.select_related('userprofile_company').all().exclude(user=user).select_related('user').order_by('-subscribed')

    content = {
        'userprofiles':userprofiles,
    }
    return render(request, 'vendroid/directory/directory.html', content)

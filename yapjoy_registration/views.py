from django.shortcuts import render, HttpResponseRedirect, Http404, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login as auth_login
from .forms import *
from yapjoy.settings import SITE_NAME
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from yapjoy_feed.models import *
from yapjoy_messages.models import Feedback
from yapjoy_registration.models import Friends
from .commons import *
from .models import *
from django.db.models import Q
from yapjoy_accounts.models import Notifications
from django.shortcuts import get_object_or_404
from django.db.models import Q
from yapjoy_messages.models import *
from yapjoy_market.models import *
import re
from django.views.decorators.csrf import csrf_exempt
from fullcalendar.util import events_to_json, calendar_options
from yapjoy_events.views import OPTIONS
from yapjoy_forum.models import Topic
import stripe
from yapjoy import settings
from billing import CreditCard, get_gateway
from datetime import datetime

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
@csrf_exempt
def friends_delete(request):
    user = request.user
    if request.method == "POST":
        id = request.GET.get('id')
        try:
            objF = AllFriends.objects.get(id=id, friends__user=user).delete()
        except:
            pass
        try:
            objF = AllFriends.objects.get(id=id, user=user).delete()
        except:
            pass
    return HttpResponseRedirect('/friends/')


@login_required(login_url='/login/')
def followers(request):
    user = request.user
    success_message = None
    all_friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile')
    followings = AllFriends.objects.filter(friends__user=user, type=AllFriends.PROFESSIONAL)
    social_post_facebook_connected = None
    #print all_friends[0].status
    try:
        #social_post_facebook = request.user.social_auth.get(provider='facebook')
        #social_post_facebook_connected = "disconnected"
        social_post_facebook_connected = "connected"
        print social_post_facebook_connected
    except Exception as e:
        print e
        social_post_facebook_connected = "disconnected"
        print social_post_facebook_connected
    context = {
        'all_friends':all_friends,
        'followings':followings,
        'user':user,
        'fb': social_post_facebook_connected,
        'success_message': success_message,
    }
    return render(request, 'vendroid/iFrame/followers.html', context)







@login_required(login_url='/login/')
def friends(request):
    user = request.user
    success_message = None
    if request.method == 'POST':
        if "accept" in request.POST or "reject" in request.POST:
            if 'accept' in request.POST:
                accept = request.POST.get('accept')
                objF = get_object_or_404(AllFriends,id=accept)
                objF.status = AllFriends.ACCEPTED
                objF.save()
                Notifications.objects.create(userprofile=objF.friends.user.userprofile, message="%s has accepted your friends request."%(objF.user.get_full_name()))
                send_email(objF.friends.user.email, message="%s has accepted your friends request."%(objF.user.get_full_name()), title="Friends request accepted", subject="Your friends request has been accepted on Yapjoy")
            if 'reject' in request.POST:
                reject = request.POST.get('reject')
                objF = get_object_or_404(AllFriends,id=reject).delete()
        elif "emails" in request.POST:
            print "in emails"
            emails = request.POST.get('emails')
            emails = emails.split(',')
            for email in emails:
                friends = None
                try:
                    friends = Friends.objects.get(user=user)
                except:
                    friends = Friends.objects.create(user=user)
                try:
                    user_offer = User.objects.get(username__iexact=email)
                    AllFriends.objects.get_or_create(friends=friends, user=user_offer)
                except:
                    print "Sending email to: ",email.strip()
                    user_new = None
                   # if re.match(r"^[a-zA-Z0-9._]+\@[a-zA-Z0-9._]+\.[a-zA-Z]{3,}$", email.strip()):
                    try:
                        print "invited_%s"%(email.strip())
                        user_new = User.objects.get_or_create(username="invited_%s"%(email.strip()), email="invited_%s"%(email.strip()))
                        AllFriends.objects.get_or_create(friends=friends, user=user_new[0], status=AllFriends.INVITED)
                    except Exception as e:
                        print e
                        return HttpResponseRedirect('')
                    context = {
                        'link':"https://www.yapjoy.com/invitation/accept/%s"%(user_new[0].email),
                        'name':request.user.get_full_name()
                    }
                    html_content = render_to_string('email/invite.html', context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives('YapJoy Invitation by %s'%(request.user.email), text_content, 'info@yapjoy.com', [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    success_message = "You have successfully sent the invitation."
                    print 'email is sent'
    all_friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile')
    followings = AllFriends.objects.filter(friends__user=user, type=AllFriends.PROFESSIONAL)
    social_post_facebook_connected = None
    #print all_friends[0].status
    try:
        #social_post_facebook = request.user.social_auth.get(provider='facebook')
        #social_post_facebook_connected = "disconnected"
        social_post_facebook_connected = "connected"
        print social_post_facebook_connected
    except Exception as e:
        print e
        social_post_facebook_connected = "disconnected"
        print social_post_facebook_connected
    context = {
        'all_friends':all_friends,
        'followings':followings,
        'user':user,
        'fb': social_post_facebook_connected,
        'success_message': success_message,
    }
    return render(request, 'vendroid/iFrame/friends.html', context)



@login_required(login_url='/login/facebook/')
def invite_friends(request):
    social_post_facebook_connected = None
    social_post_twitter_connected = None
    friends = None
    friends_invite = None

    try:
        social_post_facebook = request.user.social_auth.get(provider='facebook')
        social_post_facebook_connected = "connected"
        print social_post_facebook_connected
    except Exception as e:
        print e
        social_post_facebook_connected = "disconnected"
        print social_post_facebook_connected

    # try:
    #     social_post_twitter = request.user.social_auth.get(provider='twitter')
    #     social_post_twitter_connected = "connected"
    #     print social_post_twitter_connected
    # except Exception as e:
    #     print e
    #     social_post_twitter_connected = "disconnected"
    #     print social_post_twitter_connected

    social_user = None
    try:

        social_user = request.user.social_auth.get(provider='facebook')
        if social_user:
            url_friends = 'https://graph.facebook.com/{0}/friends?fields=id,name,picture&access_token={1}'.format(
                social_user.uid,
                social_user.extra_data['access_token'],
            )

            url_invite = 'https://graph.facebook.com/me/invitable_friends?access_token={0}'.format(
                social_user.extra_data['access_token'],
            )

            api_friends = urllib2.Request(url_friends)

            api_invite_friends = urllib2.Request(url_invite)

            friends = json.loads(urllib2.urlopen(api_friends).read()).get('data')
            friends_invite = json.loads(urllib2.urlopen(api_invite_friends).read()).get('data')

            print "friends_invite", friends_invite
            print "friends", friends
    except Exception as e:
        print e

    return render(request, 'registration/social_share.html',
                  {
                      'friends': friends,
                      'friends_invite': friends_invite,
                      'fb_connect': social_post_facebook_connected,
                      'twi_connect': social_post_twitter_connected,
                  })

@login_required(login_url='/login/')
def professionals(request):
    professionals_list = None
    user = request.user
    profile = user.userprofile
    if 'category' in request.GET:
        name = request.GET.get('category')
        if name == "Everything":
            professionals_list = UserProfile.objects.select_related('userprofile_company').filter(type=UserProfile.PROFESSIONAL).order_by('-subscribed')
        else:
            professionals_list = UserProfile.objects.select_related('userprofile_company').filter(type=UserProfile.PROFESSIONAL, looking_for__icontains=name).order_by('-subscribed')
    else:
        # if "Everything" in profile.looking_for:
        #     professionals_list = UserProfile.objects.filter(type=UserProfile.PROFESSIONAL).order_by('-subscribed')
        # else:z
        professionals_list = UserProfile.objects.select_related('userprofile_company').filter(type=UserProfile.PROFESSIONAL).order_by('-subscribed')
    categories = optionsSearch.objects.filter(status=optionsSearch.SHOW)
    return render(request, 'vendroid/iFrame/professionals.html', {
        'professionals_list':professionals_list,
        'categories':categories,
                                                                  })

@login_required(login_url='/login/')
@csrf_exempt
def professional_profile(request, id):
    professional = None
    company = None
    try:
        professional = UserProfile.objects.select_related('user').get(id=id, type=UserProfile.PROFESSIONAL)
        company = Company.objects.get(userprofile=professional)
    except Company.DoesNotExist:
        company = Company.objects.create(userprofile=professional)
    except Exception as e:
        print e
        raise Http404
    user = professional.user
    is_following = None
    try:
        is_following = AllFriends.objects.filter(user=user, friends__user_id=request.user, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING)
    except Exception as e:
        print e
        pass
    if 'follow' in request.POST:
        print 'Inside Follow'
        friends = None
        try:
            friends = Friends.objects.get(user=request.user)
        except Exception as e:
            print "Friends exception: ",e
            friends = Friends.objects.create(user=request.user)
        if not is_following:
            try:
                friend_to_add = AllFriends.objects.create(user=user, friends=friends, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING)
            except Exception as e:
                print "All friends exception: ",e
                pass
        is_following = AllFriends.objects.filter(user=user, friends__user_id=request.user, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING)
    elif 'unfollow' in request.POST:
        print "Inside unfollow"
        try:
            friends = Friends.objects.get(user=request.user)
            friend_to_add = AllFriends.objects.filter(user=user, friends=friends, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING).delete()
        except Exception as e:
            print e
        is_following = AllFriends.objects.filter(user=user, friends__user_id=request.user, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING)
    elif request.method == "POST" and "Post_comment" in request.POST:
        if request.user.userprofile == professional or is_following:
            postText = request.POST.get('Post_comment')
            image = request.FILES.get('images')
            if image:
                Post.objects.create(user=request.user,user_wall=user, text=postText, image=image)
            else:
                Post.objects.create(user=request.user,user_wall=user, text=postText)
    elif request.is_ajax() and 'feed_to_delete' in request.POST:
            print "feed to delete"
            feed_id = request.POST.get('feed_to_delete')
            # print feed_id
            if feed_id:
                Post.objects.get(id=feed_id, user=request.user).delete()
                return HttpResponse('success')

    elif request.is_ajax() and "feed_to_like" in request.POST:
            print "feed to like"
            feed_id = request.POST.get('feed_to_like')
            print "feed_id: ",feed_id
            if feed_id:
                feed = Post.objects.get(id=feed_id)
                try:
                    PostLike.objects.get(user=request.user, statuspost_id=feed_id)
                except:
                    PostLike.objects.create(user=request.user, statuspost_id=feed_id)
                    feed.likes_count += 1
                    feed.save()

                return HttpResponse(feed.likes_count)

    elif request.is_ajax() and "feed_to_fav" in request.POST:
            print "feed to fav"

            feed_fav_data = request.POST.get('feed_to_fav')
            feed_id = feed_fav_data[0]
            feed_flag = feed_fav_data[1]

            if feed_id:
                try:
                    feed_fav = Post.objects.get(id=feed_id)
                except:
                    pass

                if feed_flag == 1:
                    feed_fav.favourites.add(request.user)
                else:
                    feed_fav.favourites.remove(request.user)

                return HttpResponse('success')
    userfeed = Post.objects.filter(user_wall=user).select_related('user').order_by('-created_at')
    # .filter(Q(user=user)|Q(user=request.user))
    viewer_profile = request.user.userprofile
    picture_wall = pictureWall.objects.filter(user=user)
    bids =  Pledge.objects.select_related('product').filter(user=user)
    result_json = None
    image_url_yelp = None
    name_yelp = None
    name_categories = None
    description_yelp = None
    professional.views_count += 1
    professional.save()
    try:
        """
            Yelp open API call, upon use given srttings
        """
        if professional.yelp_name and professional.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
            location = professional.yelp_location_zip, term = professional.yelp_name, limit = 10,
            sort = YelpClient.SortType.BEST_MATCHED)
            print "result: "
            yelp_rating = result_json
            print 'Yelp: ',yelp_rating
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            name_yelp = yelp_rating['businesses'][0]['name']
            name_categories = yelp_rating['businesses'][0]['categories'][0]
            description_yelp = yelp_rating['businesses'][0]['snippet_text']
    except Exception as e:
        print e
        pass
    context = {
        'professional':professional,
        'company':company,
        'userfeed':userfeed,
        'user':user,
        'profile':viewer_profile,
        'is_following':is_following,
        'form':imageForm(),
        'picture_wall':picture_wall,
        'bids':bids,
        'result_json':result_json,
        'image_url_yelp':image_url_yelp,
        'name_yelp':name_yelp,
        'description_yelp':description_yelp,
        'name_categories':name_categories,
    }
    return render(request, 'vendroid/profile/professional_profile_V3.html', context)

@login_required(login_url='/login/')
def events(request):
    return render(request, 'iFrame/events.html')

@login_required(login_url='/login/')
def tasks(request):
    return render(request, 'iFrame/tasks.html')

@login_required(login_url='/login/')
def recommend(request):
    return render(request, 'iFrame/recommend.html')

@login_required(login_url='/login/')
def seatingCharts(request):
    return render(request, 'vendroid/seating/seating_plan.html')
import requests
import json
from instagram.client import InstagramAPI
@login_required(login_url='/login/')
def instagram(request):
    user = request.user
    profile = user.userprofile
    if "code" in request.GET:
        code = request.GET['code']
        #  curl -F 'client_id=CLIENT_ID' \
        # -F 'client_secret=CLIENT_SECRET' \
        # -F 'grant_type=authorization_code' \
        # -F 'redirect_uri=AUTHORIZATION_REDIRECT_URI' \
        # -F 'code=CODE' \
        # https://api.instagram.com/oauth/access_token
        print 'code: ',code
        data_send = {
                     'client_id': "89cbeff80dbb433e8ac79e180bf5a58f",
                     'client_secret': "9822fe17c14442ebbfd0d0dfe9b38fc9",
                     'grant_type': "authorization_code",
                     'scope': "public_content",
                     'redirect_uri': "https://www.yapjoy.com/instagram/",
                     'code': code,
                     }
        print data_send
        print "before r"
        r = requests.post("https://api.instagram.com/oauth/access_token", data=data_send)
        print r
        print "text", r.text
        res = json.loads(r.text)
        print res
        response = None
        access_token = res['access_token']
        user_id = res['user']['id']
        print 'access token: ',access_token
        print 'user_id: ',user_id
        profile.instagram_access_token = access_token
        profile.instagram_user_id = user_id
        profile.save()
        return HttpResponseRedirect('/')
    else:
        if profile.instagram_access_token and profile.instagram_user_id:
            try:
                access_token = profile.instagram_access_token.split()
                print 'access token: ',access_token
                client_secret = "9822fe17c14442ebbfd0d0dfe9b38fc9"
                print client_secret
                print profile.user_id
                print 'access token: ',access_token[0]
                api_inst = InstagramAPI(access_token=access_token, client_secret=client_secret)
                print 'API is called'
                recent_media, next_ = api_inst.user_recent_media(user_id=profile.instagram_user_id, count=10)
                print 'recent media'
                photos = []
                for media in recent_media:
                    photos.append('<img src="%s"/>' % media.images['thumbnail'].url)
                print photos
                print 'done'
                # popular_media = api_inst.media_popular(user_id='331304423',count=20)
                # for media in popular_media:
                #     print media.images['standard_resolution'].url
            except Exception as e:
                profile.instagram_access_token = ""
                profile.instagram_user_id = ""
                profile.save()
                print 'Exception'
                print e
        print "NO code found"
    return render(request, 'vendroid/iFrame/instagram.html',{
        'images':photos,
        # 'popular_media':popular_media,
    })

from yapjoy_tasks.models import Task
from yapjoy_events.models import CalendarEvent
from yapjoy_feed.forms import pictureWallForm
@login_required(login_url='/login/')
@csrf_exempt
def dashboard(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.UNKNOWNPROFILE:
        return HttpResponseRedirect('/choose_profile/')
    companyform = None
    profileform = None
    company = None
    if profile.type == UserProfile.PROFESSIONAL:
        pass
        # company = Company.objects.get(userprofile=profile)
        # initial_company = {
        #     'name':company.name,
        #     'description':company.description,
        #     'employees':company.employees,
        #     'payment_terms':company.payment_terms,
        # }
        # companyform = companyForm(initial=initial_company)
    else:
        initial_profile = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'age':profile.age,
            'gender':profile.gender,
            'wedding_date':profile.wedding_date,
            'street':profile.street,
            'city':profile.city,
            'state':profile.state,
            'zip':profile.zip,
            'looking_for':profile.looking_for,
        }
        profileform = profileUpdateForm(initial=initial_profile)
    if 'Post_comment' in request.POST:
        print 'works'
        postText = request.POST.get('Post_comment')
        images = request.FILES.get('images')
        if images:
            post = Post.objects.create(user=user,user_wall=user, text=postText, image=images)
        else:
            post = Post.objects.create(user=user,user_wall=user, text=postText)
        print post
        return HttpResponseRedirect('')
    elif 'profileform' in request.POST:
        profileform = profileUpdateForm(request.POST, request.FILES)
        if profileform.is_valid():
            data = profileform.cleaned_data
            first_name = data['first_name']
            last_name = data['last_name']
            gender = data['gender']
            age = data['age']
            wedding_date = data['wedding_date']
            street = data['street']
            city = data['city']
            state = data['state']
            zip = data['zip']
            looking_for = request.POST.getlist('assigned_to')
            print looking_for
            # looking_for = data['looking_for']
            # print looking_for
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profile.gender = gender
            profile.wedding_date = wedding_date
            if wedding_date:
                try:
                    wed_cal = CalendarEvent.objects.get(user=user, is_wedding=True)
                    wed_cal.start = wedding_date
                    wed_cal.end = wedding_date
                    wed_cal.save()
                except Exception as e:
                    print e
                    CalendarEvent.objects.create(title="Wedding Day", user=user, is_wedding=True, start=wedding_date, end=wedding_date, all_day=True)
            profile.street = street
            profile.city = city
            profile.state = state
            profile.zip = zip
            profile.age = age
            print "Looking for: ",looking_for
            #profile.looking_for = looking_for
            if looking_for:
                looking_for_string = ""
                optionsSearch_users.objects.filter(userprofile = profile).delete()
                for o in looking_for:
                    osu = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                    looking_for_string += "%s "%(osu.open_search.name)
                profile.looking_for = looking_for_string
            profile.save()
            successMessage = 'Profile edited successfully.'
            print successMessage
    elif 'companyform' in request.POST:
        companyform = companyForm(request.POST)
        if companyform.is_valid():
            data = companyform.cleaned_data
            name = data['name']
            description = data['description']
            employees = data['employees']
            payment_terms = data['payment_terms']
            print name
            print description
            print employees
            print payment_terms

            company.name = name
            company.description = description
            company.employees = employees
            company.payment_terms = payment_terms
            company.save()
    elif request.is_ajax() and 'feed_to_delete' in request.POST:
            print "feed to delete"
            feed_id = request.POST.get('feed_to_delete')
            # print feed_id
            if feed_id:
                Post.objects.get(id=feed_id, user_wall=request.user).delete()
                return HttpResponse('success')

    elif request.is_ajax() and "feed_to_like" in request.POST:
            print "feed to like"
            feed_id = request.POST.get('feed_to_like')
            if feed_id:
                feed = Post.objects.get(id=feed_id, user_wall=request.user)
                try:
                    PostLike.objects.get(user=request.user, statuspost_id=feed_id)
                except:
                    PostLike.objects.create(user=request.user, statuspost_id=feed_id)
                    feed.likes_count += 1
                    feed.save()

                return HttpResponse(feed.likes_count)

    elif request.is_ajax() and "feed_to_fav" in request.POST:
            print "feed to fav"
            feed_fav = None
            feed_fav_data = request.POST.get('feed_to_fav')
            feed_id = feed_fav_data[0]
            feed_flag = feed_fav_data[1]

            if feed_id:
                try:
                    feed_fav = Post.objects.get(id=feed_id)
                except:
                    pass

                if feed_flag == 1:
                    feed_fav.favourites.add(request.user)
                else:
                    feed_fav.favourites.remove(request.user)

                return HttpResponse('success')
    elif "dashboardlink" in request.POST:
        print 'inside dashboard link'
        dashboard_link = request.POST.get('dashboardlink')
        profile.dashboard_link = dashboard_link
        profile.save()
        print profile.dashboard_link
    elif "picture" in request.POST or "picture" in request.FILES:
        print 'inside picture wall'
        pictureWall_Form =  pictureWallForm(request.POST, request.FILES)
        if pictureWall_Form.is_valid():
            data = pictureWall_Form.cleaned_data
            pictureWall.objects.create(picture=data['picture'], user=user)
            print 'image is uploaded'
    elif "image_send" in request.POST:
        print 'inside IMAGE POST'
        image_send = request.POST.get('image_send')
        print image_send
        import urllib
        # pw = pictureWall.objects.create(user=user)

        # i_name = "yj_image_%s.jpg"%(pw.id)
        # img_sender = urllib.urlretrieve(image_send, i_name)
        # pw.picture = "/yj_image_%s.jpg"%(pw.id)
        # pw.save()


        import urllib
        from urlparse import urlparse
        from django.core.files import File

        img_url = image_send#'http://www.site.com/image.jpg'

        # photo = pictureWall()    # set any other fields, but don't commit to DB (ie. don't save())
        name = urlparse(img_url).path.split('/')[-1]
        content = urllib.urlretrieve(img_url)

        # See also: http://docs.djangoproject.com/en/dev/ref/files/file/
        # pw.picture.save(name, File(open(content[0])), save=True)
        post = Post.objects.create(user=user,user_wall=user, text="Shared a picture")
        post.image.save(name, File(open(content[0])), save=True)


    friends_following = []
    # if not profile.type == UserProfile.PROFESSIONAL:
    friends_following = AllFriends.objects.filter(Q(friends__user=user, status=AllFriends.ACCEPTED)|Q(friends__user=user, status=AllFriends.FOLLWOING)|Q(user=user, status=AllFriends.ACCEPTED)|Q(user=user, status=AllFriends.FOLLWOING)).values_list('user',flat=True)#.select_related('user').values('user')
    #print 'friends following: ',friends_following
    userfeed = []
    if request.GET.get('view_all'):
        up = Post.objects.filter(Q(user_wall=user)|Q(user_wall__in=friends_following)).select_related('user','user__userprofile','user_wall','user_wall__userprofile').order_by('-created_at')
        if up:
            for upi in up:
                userfeed.append({
                    'type':'post',
                    'image_url':upi.user.userprofile.get_image_url,
                    'text':upi.text,
                    'url':upi.user.userprofile.get_profile_url,
                    'time':upi.created_at,
                    'name':upi.user.get_full_name,
                })
    else:
        up = Post.objects.filter(Q(user_wall=user)|Q(user_wall__in=friends_following)).select_related('user','user__userprofile').order_by('-created_at')[:8]
        if up:
            for upi in up:
                userfeed.append({
                    'type': 'post',
                    'image_url': upi.user.userprofile.get_image_url,
                    'text': upi.text,
                    'url': upi.user.userprofile.get_profile_url,
                    'time': upi.created_at,
                    'name': upi.user.get_full_name,
                })
    #print userfeed
    # recommend = None
    # if not profile.type == UserProfile.PROFESSIONAL:
    #     recommend = UserProfile.objects.all().exclude(id=profile.id).order_by('-subscribed','-created_at').select_related('user').values('user','user__first_name','user__last_name','type','id')[:4]
    #print recommend
    tasks = Task.objects.filter(user=user).select_related('user','user__userprofile')[:4]
    # .only('id','complete','subject')

    if tasks:
        for task in tasks:
            userfeed.append({
                'type': 'task',
                'image_url': task.user.userprofile.get_image_url,
                'text': task.subject,
                'url': task.user.userprofile.get_profile_url,
                'time': task.created_at,
                'name': task.user.get_full_name,
            })
    events = CalendarEvent.objects.filter(user=request.user).values('id','title','start')[:4]

    if events:
        event_list_append = CalendarEvent.objects.filter(user=user).select_related(
            'user','user__userprofile'
        )
        print 'events are here: ', event_list_append
        for event_i in event_list_append:
            userfeed.append({
                'type': 'event',
                'image_url': event_i.user.userprofile.get_image_url,
                'text': event_i.title,
                'url': event_i.user.userprofile.get_profile_url,
                'time': event_i.created_at,
                'name': event_i.user.get_full_name,
            })
            # print len(userfeed)
            # print userfeed
    if userfeed:
        userfeed = sorted(userfeed, key=lambda k: k['time'], reverse=True)
    looking_for = None
    looking_for_selected = None
    if not profile.wedding_date:
        looking_for = optionsSearch.objects.all().only('id','name')
        looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search').only('open_search_id','open_search__name')
        if looking_for_selected:
            looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search_id'))
        # print looking_for_selected
        # print looking_for
    tasks_count = Task.objects.filter(user=request.user).count()
    suggestions = None
    services = None
    try:
        if profile.type == "Professional":
            services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            if "Honeymoon & Travel" in services:
                services.append('Everything')
            if services:
                subscriptioncodes_ids = SubscriptionCode.objects.filter(is_registered=False).values_list('user_id',flat=True)
                suggestions = UserProfile.objects.filter(reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)), ~Q(type__iexact=UserProfile.PROFESSIONAL)).exclude(user__id__in=subscriptioncodes_ids)[:10]#.exclude(user=user)
        else:
            services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            if services:
                suggestions = UserProfile.objects.select_related('userprofile_company').filter(reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)), type__iexact=UserProfile.PROFESSIONAL)[:10]#.exclude(user=user)
        plans_count = 0
        if profile.type == UserProfile.PROFESSIONAL:
            # services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            # print "Services: ",services
            # for aaa in services:
            #     print "Service: ",aaa
            # if services:
            #     plans_count = Product.objects.filter(Q(reduce(operator.or_, (Q(description__icontains=x) for x in services))),status=Product.ACTIVE, is_completed=False).count()
            if services:
                plans_count = Product.objects.filter(status=Product.ACTIVE).filter(category__name__in=services).count()
                print 'plans count ', plans_count
        else:
            plans_count = Product.objects.filter(user=request.user).count()
    except:
        pass
    events_count = CalendarEvent.objects.filter(user=request.user).count()
    friends_count = 0
    if profile.type == UserProfile.PROFESSIONAL:
        friends_count = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).count()
    else:
        friends_count = AllFriends.objects.filter(Q(friends__user=user, status=AllFriends.ACCEPTED) | Q(friends__user=user, status=AllFriends.FOLLWOING) | Q(user=user, status=AllFriends.ACCEPTED) | Q(user=user, status=AllFriends.FOLLWOING)).count()
    pledge_count = Pledge.objects.filter(user=user).count()
    tasks_user = Task.objects.filter(user=request.user)
    completed_task_count=tasks_user.filter(complete=True).count()
    task_count=tasks_user.count()
    rsvp_count = RsvpCount.objects.get_or_create(user=user)
    # picture_wall = pictureWall.objects.filter(user=user)

    rsvp_count = rsvp_count[0]
    rsvp_percentage = 0
    if rsvp_count.rsvp_accepted_count>0 and rsvp_count.rsvp_count>0:
        rsvp_percentage = (rsvp_count.rsvp_accepted_count*100)/rsvp_count.rsvp_count
        print 'rsvp pe',rsvp_percentage
    else:
        rsvp_percentage = 0

    tasks_percentage = 0
    topics = Topic.objects.all().select_related('forum','creator','creator__userprofile').order_by("-created")
    if task_count>0 and completed_task_count>0:
        tasks_percentage = (completed_task_count*100)/task_count
    else:
        tasks_percentage = 0
    bids_count = 0
    bids_awarded = 0
    if profile.type == UserProfile.PROFESSIONAL:
        bids_count = Pledge.objects.filter(user=user).count()
        bids_awarded = Pledge.objects.filter(user=user, is_awarded=True).count()
    show_dialogue = None
    show_dialogue_code = False
    sub = False
    # try:
    #     sub = SubscriptionCode.objects.get(user=user)
    # except:
    #     sub = SubscriptionCode.objects.create(user=user, code=id_generator())
    # if not sub.is_subscribed and (profile.type == UserProfile.BRIDE or profile.type == UserProfile.GROOM):
    #     show_dialogue = "True"
    #     show_dialogue_code = sub.code
    picture_wall = Post.objects.filter(Q(Q(user_wall=user)|Q(user_wall__in=friends_following))&~Q(image="")).select_related('user','user__userprofile','user_wall','user_wall__userprofile').order_by('-created_at')
    photos = []
    # if profile.instagram_access_token and profile.instagram_user_id:
    #     try:
    #         access_token = profile.instagram_access_token.split()
    #         print 'access token: ',access_token
    #         client_secret = "9822fe17c14442ebbfd0d0dfe9b38fc9"
    #         print client_secret
    #         print profile.user_id
    #         print 'access token: ',access_token[0]
    #         api_inst = InstagramAPI(access_token=access_token[0], client_secret=client_secret)
    #         print 'API is called'
    #         recent_media, next_ = api_inst.user_recent_media(user_id=profile.instagram_user_id, count=10)
    #         print 'recent media'
    #         # photos = []
    #         for media in recent_media:
    #             photos.append('<img src="%s"/>' % media.images['thumbnail'].url)
    #         print photos
    #         print 'done'
    #         # popular_media = api_inst.media_popular(user_id='331304423',count=20)
    #         # for media in popular_media:
    #         #     print media.images['standard_resolution'].url
    #     except Exception as e:
    #         print 'Exception'
    #         print e
    content = {
        'bids_count':bids_count,
        'bids_awarded':bids_awarded,
        'topics':topics,
        'plans_count':plans_count,
        'suggestions':suggestions,
        'rsvp_count':rsvp_count,
        'rsvp_percentage':rsvp_percentage,
        'userfeed':userfeed,
        'profile':profile,
        'company':company,
        'user':user,
        'tasks_count':tasks_count,
        'picture_wall':picture_wall,
        'pictureWallForm':pictureWallForm(),
        'events_count':events_count,
        'friends_count':friends_count,
        'pledge_count':pledge_count,
        # 'recommend':recommend,
        'profileform':profileform,
        'companyform':companyform,
        'tasks':tasks,
        'events':events,
        'looking_for_selected':looking_for_selected,
        'looking_for':looking_for,
        'tasks_percentage':tasks_percentage,
        'task_count':task_count,
        'completed_task_count':completed_task_count,
        'jquery_min': True,
        'show_dialogue': show_dialogue,
        'photos': photos,
        'show_dialogue_code': show_dialogue_code,
        'calendar_config_options': calendar_options('/events/all_events/', OPTIONS),
    }
    return render(request, 'vendroid/iFrame/dashboardV2.html', content)

@login_required(login_url='/login/')
@csrf_exempt
def all_leads(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.UNKNOWNPROFILE:
        return HttpResponseRedirect('/choose_profile/')
    elif not profile.type == UserProfile.PROFESSIONAL:
        return HttpResponseRedirect('/')

    suggestions = None
    services = None
    try:
        if profile.type == "Professional":
            services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            if services:
                suggestions = UserProfile.objects.filter(reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)), ~Q(type__iexact=UserProfile.PROFESSIONAL))[:200]#.exclude(user=user)
    except:
        pass
    content = {
        'profile':profile,
        'user':user,
        'suggestions':suggestions,
        'jquery_min': True,
    }
    return render(request, 'vendroid/potential_leads/all_leads.html', content)




def dashboardTest(request):
    user = User.objects.get(id=1)
    profile = user.userprofile
    if profile.type == UserProfile.UNKNOWNPROFILE:
        return HttpResponseRedirect('/choose_profile/')
    companyform = None
    profileform = None
    company = None
    if profile.type == UserProfile.PROFESSIONAL:
        company = Company.objects.get(userprofile=profile)
        initial_company = {
            'name':company.name,
            'description':company.description,
            'employees':company.employees,
            'payment_terms':company.payment_terms,
        }
        companyform = companyForm(initial=initial_company)
    else:
        initial_profile = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'age':profile.age,
            'gender':profile.gender,
            'wedding_date':profile.wedding_date,
            'street':profile.street,
            'city':profile.city,
            'state':profile.state,
            'zip':profile.zip,
            'looking_for':profile.looking_for,
        }
        profileform = profileUpdateForm(initial=initial_profile)
    if 'Post_comment' in request.POST:
        print 'works'
        postText = request.POST.get('Post_comment')
        images = request.FILES.get('images')
        if images:
            post = Post.objects.create(user=user,user_wall=user, text=postText, image=images)
        else:
            post = Post.objects.create(user=user,user_wall=user, text=postText)
        print post
        return HttpResponseRedirect('')
    elif 'profileform' in request.POST:
        profileform = profileUpdateForm(request.POST, request.FILES)
        if profileform.is_valid():
            data = profileform.cleaned_data
            first_name = data['first_name']
            last_name = data['last_name']
            gender = data['gender']
            age = data['age']
            wedding_date = data['wedding_date']
            street = data['street']
            city = data['city']
            state = data['state']
            zip = data['zip']
            looking_for = request.POST.getlist('assigned_to')
            print looking_for
            # looking_for = data['looking_for']
            # print looking_for
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profile.gender = gender
            profile.wedding_date = wedding_date
            if wedding_date:
                try:
                    wed_cal = CalendarEvent.objects.get(user=user, is_wedding=True)
                    wed_cal.start = wedding_date
                    wed_cal.end = wedding_date
                    wed_cal.save()
                except Exception as e:
                    print e
                    CalendarEvent.objects.create(title="Wedding Day", user=user, is_wedding=True, start=wedding_date, end=wedding_date, all_day=True)
            profile.street = street
            profile.city = city
            profile.state = state
            profile.zip = zip
            profile.age = age
            print "Looking for: ",looking_for
            #profile.looking_for = looking_for
            if looking_for:
                looking_for_string = ""
                optionsSearch_users.objects.filter(userprofile = profile).delete()
                for o in looking_for:
                    osu = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                    looking_for_string += "%s "%(osu.open_search.name)
                profile.looking_for = looking_for_string
            profile.save()
            successMessage = 'Profile edited successfully.'
            print successMessage
    elif 'companyform' in request.POST:
        companyform = companyForm(request.POST)
        if companyform.is_valid():
            data = companyform.cleaned_data
            name = data['name']
            description = data['description']
            employees = data['employees']
            payment_terms = data['payment_terms']
            print name
            print description
            print employees
            print payment_terms

            company.name = name
            company.description = description
            company.employees = employees
            company.payment_terms = payment_terms
            company.save()
    elif request.is_ajax() and 'feed_to_delete' in request.POST:
            print "feed to delete"
            feed_id = request.POST.get('feed_to_delete')
            # print feed_id
            if feed_id:
                Post.objects.get(id=feed_id, user_wall=user).delete()
                return HttpResponse('success')

    elif request.is_ajax() and "feed_to_like" in request.POST:
            print "feed to like"
            feed_id = request.POST.get('feed_to_like')
            if feed_id:
                feed = Post.objects.get(id=feed_id, user_wall=user)
                try:
                    PostLike.objects.get(user=user, statuspost_id=feed_id)
                except:
                    PostLike.objects.create(user=user, statuspost_id=feed_id)
                    feed.likes_count += 1
                    feed.save()

                return HttpResponse(feed.likes_count)

    elif request.is_ajax() and "feed_to_fav" in request.POST:
            print "feed to fav"
            feed_fav = None
            feed_fav_data = request.POST.get('feed_to_fav')
            feed_id = feed_fav_data[0]
            feed_flag = feed_fav_data[1]

            if feed_id:
                try:
                    feed_fav = Post.objects.get(id=feed_id)
                except:
                    pass

                if feed_flag == 1:
                    feed_fav.favourites.add(user)
                else:
                    feed_fav.favourites.remove(user)

                return HttpResponse('success')
    friends_following = []
    # if not profile.type == UserProfile.PROFESSIONAL:
    friends_following = AllFriends.objects.filter(Q(friends__user=user, status=AllFriends.ACCEPTED)|Q(friends__user=user, status=AllFriends.FOLLWOING)|Q(user=user, status=AllFriends.ACCEPTED)|Q(user=user, status=AllFriends.FOLLWOING)).select_related('user').values('user')
    #print 'friends following: ',friends_following
    userfeed = None
    if request.GET.get('view_all'):
        userfeed = Post.objects.filter(Q(user_wall=user)|Q(user_wall__in=friends_following)).select_related('user','user__userprofile','user_wall','user_wall__userprofile').order_by('-created_at')
    else:
        userfeed = Post.objects.filter(Q(user_wall=user)|Q(user_wall__in=friends_following)).select_related('user','user__userprofile','user_wall','user_wall__userprofile').order_by('-created_at')[:8]
    #print userfeed
    recommend = None
    if not profile.type == UserProfile.PROFESSIONAL:
        recommend = UserProfile.objects.all().exclude(id=profile.id).order_by('-subscribed','-created_at').select_related('user').values('user','user__first_name','user__last_name','type','id')[:4]
    #print recommend
    tasks = Task.objects.filter(user=user).values('id','complete','subject')[:4]
    events = CalendarEvent.objects.filter(user=user).values('id','title','start')[:4]
    looking_for = None
    looking_for_selected = None
    if not profile.wedding_date:
        looking_for = optionsSearch.objects.all()
        looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search')
        if looking_for_selected:
            looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search'))
        # print looking_for_selected
        # print looking_for
    content = {
        'userfeed':userfeed,
        'profile':profile,
        'company':company,
        'user':user,
        'recommend':recommend,
        'profileform':profileform,
        'companyform':companyform,
        'tasks':tasks,
        'events':events,
        'looking_for_selected':looking_for_selected,
        'looking_for':looking_for,
    }
    return render(request, 'iFrame/dashboard.html', content)

@login_required(login_url='/login/')
def notifications(request):
    userprofile = request.user.userprofile
    if userprofile.notification_count > 0:
        userprofile.notification_count = 0
        userprofile.save()
    notifications = Notifications.objects.filter(userprofile=userprofile).select_related('userprofile','userprofile__user').order_by('-created_at')
    context = {
        'notifications':notifications,
    }
    return render(request, 'vendroid/iFrame/notifications.html', context)



@login_required(login_url='/login/')
def feedback(request):
    form = feedbackForm()
    success = None
    if request.method == 'POST':
        form = feedbackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            Feedback.objects.create(user=request.user, subject=subject, message=message)
            success = True
            try:
                # message = 'a ew'%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                send_email(sendTo='info@yapjoy.com', title=subject, message=message, subject="YapJoy - Feedback by %s"%(request.user.email))
                send_email(sendTo='adeelpkpk@gmail.com', title=subject, message=message, subject="YapJoy - Feedback by %s"%(request.user.email))
            except Exception as e:
                print e
            form = feedbackForm()
    context = {
        'form':form,
        'success':success,
    }
    return render(request, 'vendroid/iFrame/feedback.html', context)\





@login_required(login_url='/login/')
def support(request):
    form = supportForm()
    success = None
    if request.method == 'POST':
        form = supportForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            Feedback.objects.create(user=request.user, subject=subject, message=message)
            success = True
            try:
                # message = 'a ew'%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                # send_email(sendTo='info@yapjoy.com', title=subject, message=message, subject="YapJoy - Feedback by %s"%(request.user.email))
                send_email(sendTo='adeelpkpk@gmail.com', title=subject, message=message, subject="YapJoy - Feedback by %s"%(request.user.email))
            except Exception as e:
                print e
            form = supportForm()
    context = {
        'form':form,
        'success':success,
        # 'id':id,
    }
    return render(request, 'vendroid/iFrame/support.html', context)




@login_required(login_url='/login/')
def recommendations(request):
    # recommend = get_recommend_users(request, request.user)
    user  = request.user
    profile = user.userprofile
    suggestions = None
    try:
        if profile.type == "Professional":
            services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            if "Honeymoon & Travel" in services:
                services.append('Everything')
            if services:
                subscriptioncodes_ids = SubscriptionCode.objects.filter(is_registered=False).values_list('user_id',flat=True)
                suggestions = UserProfile.objects.select_related('userprofile_company').filter(reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)), ~Q(type__iexact=UserProfile.PROFESSIONAL)).exclude(user__id__in=subscriptioncodes_ids)#.filter(sub_code__is_registered=True)#.exclude(user=user)
        else:
            services = list(optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
            if services:
                suggestions = UserProfile.objects.filter(reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)), type__iexact=UserProfile.PROFESSIONAL).order_by('-last_seen')#.exclude(user=user)
    except:
        pass
    context = {
        'recommend':suggestions
    }
    return render(request, 'vendroid/iFrame/recommendation.html', context)

def unsubscribeuser(request, code):
    user = None
    try:
        usemail = RegisteredBrideUsers.objects.get(code=code)
        usemail.is_unsub = True
        usemail.save()
        user = User.objects.get(email=usemail.email)
        user.delete()
        return render(request, 'registration/user_deleted.html')
    except:
        raise Http404


@login_required(login_url='/login/')
def choose_profile(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.UNKNOWNPROFILE:
        form = ProfileSelectForm()
        if request.POST:
            form = ProfileSelectForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                type = data['type']
                profile.type = type
                profile.save()
                return HttpResponseRedirect('/')
        return render(request, 'vendroid/registration/choose_profile.html',{'form':form,
                                                                   'user':user,})
    else:
        return HttpResponseRedirect('/')

def invite_accept(request, email):
    try:
        print email
        user = User.objects.get(email=email)
        print user
        friends = AllFriends.objects.filter(user=user, status=AllFriends.INVITED)[0]
        print friends
        form = ProfileCreateForm()
        if request.POST:
            form = ProfileCreateForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                email = data['email']
                password = data['password']
                first_name = data['first_name']
                last_name = data['last_name']
                type = data['type']
                user.username = email
                user.last_name = last_name
                user.first_name = first_name
                user.email = email
                user.set_password(password)
                user.save()
                profile = user.userprofile
                profile.type = type
                profile.save()
                friends.status=AllFriends.ACCEPTED
                friends.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                return HttpResponseRedirect('/')
        print "showing form"
        return render(request, 'registration/profile_creation_form.html',{'form':form,
                                                                   'user':user,})
    except Exception as e:
        print e
        raise Http404




@login_required(login_url='/login/')
@csrf_exempt
def wall_feed_ajax(request, index):
    user = request.user
    profile = user.userprofile
    userfeed = None
    try:
        userfeed = Post.objects.filter(user=user).order_by('-created_at')[str(index):str(int(index)+3)]
    except Exception as e:
        print e
    return render(request, 'vendroid/partial/_user_feed_ajax.html',{
        'userfeed':userfeed,
        'profile':profile,
    })


from yapjoy_vendors.models import VendorRegistration
@login_required(login_url='/login/')
@csrf_exempt
def bg_event_create(request):
    return render(request, 'vendroid/demov2/vendors/profile/yapjoy_event/yapjoy_event_detail.html')

from yapjoy_registration.forms import ProfileFormNew
@login_required(login_url='/login/')
@csrf_exempt
def bg_profile(request):
    string = ''
    user = UserProfile.objects.get(user=request.user)
    vendor = None
    try:
        vendor = VendorRegistration.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/login/')
    if request.is_ajax():
        print "ajax call"
        """Feed Back"""
        if request.method == 'GET' and request.GET.get('action') == 'feedback':
            print "feedback: "
            strusering = render_to_string('vendroid/demov2/profile/partials/_feedback.html', {

            })
            return HttpResponse(strusering)
        elif 'feedback' in request.POST:
            print "take feedback"
            message = request.POST.get('feedback')
            feedback = Feedback.objects.create(user=request.user, subject='test', message=message)
            success = True
            try:
                # message = 'a ew'%(user.user.get_full_name())
                send_email(sendTo='mbnysf11@gmail.com', title='Feedback', message=message,
                           subject="YapJoy - Feedback by %s" % (request.user.email))

                send_email(sendTo='info@yapjoy.com', title='Feedback', message=message,
                           subject="YapJoy - Feedback by %s" % (request.user.email))

                send_email(sendTo='adeelpkpk@gmail.com', title='test', message=message,
                           subject="YapJoy - Feedback by %s" % (request.user.email))

                string = render_to_string('vendroid/demov2/profile/partials/_feedback_success.html', {
                    'u': user,
                    'feedback':feedback
                })
                return HttpResponse(string)
            except Exception as e:
                print e

            string = render_to_string('vendroid/demov2/profile/partials/_mainpage.html', {
                'u': user
            })
            return HttpResponse(string)
        """Edit Profile"""
        if request.method == 'GET' and request.GET.get('action') == 'profile':
            print "profile"

            print "user: ", user
            string = render_to_string('vendroid/demov2/profile/partials/_profile.html', {
                'u':user,
                'vendor':vendor
            })
            return HttpResponse(string)
        if request.method == 'GET' and request.GET.get('action') == 'edit_profile':
            print "edit profile"

            form = ProfileFormNew(initial={
                'profession':user.profession,
                'image':user.image,
                'first_name':user.user.first_name,
                'last_name':user.user.last_name,
                'phone':user.phone,
            })
            string = render_to_string('vendroid/demov2/profile/partials/_edit_profile.html', {
                'u' : user,
                'vendor' : vendor,
                'form' : form
            })
            return HttpResponse(string)
        if request.method == 'POST' and 'profile_edit_form_singal' in request.POST:
            print "edit profile POST"
            print request.POST
            print request.FILES
            form = ProfileFormNew(request.POST, request.FILES)
            if form.is_valid():
                print form.cleaned_data
                data = form.cleaned_data
                user.profession = data['profession']
                if request.FILES.get('image'):
                    user.image = data['image']
                user.phone = data['phone']
                user.save()
                user_obj = user.user
                # first_name, last_name = data['name'].split(' ')
                user_obj.first_name = data['first_name']
                user_obj.last_name = data['last_name']
                user_obj.save()
                print 'all saved'
                string = render(request, 'vendroid/demov2/profile/partials/_mainpage.html', {
                    'u': user
                })
                return HttpResponse(string)
            else:
                print "form is invalid"
                print form.errors
            # full_name = request.POST.get('edit_full_name')
            # role = request.POST.get('edit_role')
            # email = request.POST.get('edit_email')
            # phone = request.POST.get('edit_phone')
            # # if request.FILES:
            # image = request.FILES.get('edit_image')
            # print "useredit: ", full_name, role, email, phone, image
            # usr = User.objects.get(username=email)
            # print "u: ", usr
            # usr.first_name = full_name.split(' ')[0]
            # usr.last_name = full_name.split(' ')[1]
            # usr.email = email
            # usr.username = email
            # usr.save()
            # user.user.first_name = full_name.split(' ')[0]
            # user.user.last_name = full_name.split(' ')[1]
            # user.user.email = email
            # user.phone = phone
            # user.user.save()
            # user.image = image
            # user.profession = role
            # user.save()

            string = render(request, 'vendroid/demov2/profile/partials/_mainpage.html', {
                'u': user
            })
            return HttpResponse(string)

        """Notification"""
        if request.method == 'GET' and request.GET.get('action') == 'notification':
            print "edit profile"
            string = render_to_string('vendroid/demov2/profile/partials/_notification.html', {
                'u': user
            })
            return HttpResponse(string)
        elif request.method == 'POST' and request.POST.get('action') == 'notification':
            print "notification"
            direct = request.POST.get('direct')
            channel = request.POST.get('channel')
            daily = request.POST.get('daily')
            weekly = request.POST.get('weekly')
            print "notification: ",(direct), channel, daily, weekly
            if weekly == 'true':
                user.weekly = True
            elif weekly == 'false':
                user.weekly = False

            if daily == 'true':
                user.daily = True
            elif daily == 'false':
                user.daily = False

            if direct == 'true':
                user.direct = True
            elif direct == 'false':
                user.direct = False

            if channel == 'true':
                user.channel = True
            elif channel == 'false':
                user.channel = False
            user.save()

            string = render_to_string('vendroid/demov2/profile/partials/_mainpage.html', {
                'u': user
            })
            return HttpResponse(string)

    else:
        print "not ajax"
    return render(request, "vendroid/demov2/profile/bg_profile.html", {'u':user})

@login_required(login_url='/login/')
@csrf_exempt
def profile(request):
    user = request.user
    profile = user.userprofile
    if request.method == "POST" and "Post_comment" in request.POST:
        postText = request.POST.get('Post_comment')
        image = request.FILES.get('image')
       # print image
        if image:
            Post.objects.create(user=user,user_wall=user, text=postText, image=image)
        else:
            Post.objects.create(user=user,user_wall=user, text=postText)
        return HttpResponseRedirect('')
    elif request.is_ajax() and 'feed_to_delete' in request.POST:
            print "feed to delete"
            feed_id = request.POST.get('feed_to_delete')
            # print feed_id
            if feed_id:
                Post.objects.get(id=feed_id, user_wall=request.user).delete()
                return HttpResponse('success')

    elif request.is_ajax() and "feed_to_like" in request.POST:
            print "feed to like"
            feed_id = request.POST.get('feed_to_like')
            if feed_id:
                feed = Post.objects.get(id=feed_id, user_wall=request.user)
                try:
                    PostLike.objects.get(user=request.user, statuspost_id=feed_id)
                except:
                    PostLike.objects.create(user=request.user, statuspost_id=feed_id)
                    feed.likes_count += 1
                    feed.save()

                return HttpResponse(feed.likes_count)

    elif request.is_ajax() and "feed_to_fav" in request.POST:
            print "feed to fav"

            feed_fav_data = request.POST.get('feed_to_fav')
            feed_id = feed_fav_data[0]
            feed_flag = feed_fav_data[1]

            if feed_id:
                try:
                    feed_fav = Post.objects.get(id=feed_id)
                except:
                    pass

                if feed_flag == 1:
                    feed_fav.favourites.add(request.user)
                else:
                    feed_fav.favourites.remove(request.user)

                return HttpResponse('success')
    elif "picture" in request.POST or "picture" in request.FILES:
        print 'inside picture wall'
        pictureWall_Form =  pictureWallForm(request.POST, request.FILES)
        if pictureWall_Form.is_valid():
            data = pictureWall_Form.cleaned_data
            pictureWall.objects.create(picture=data['picture'], user=user)
            print 'image is uploaded'

    userfeed = Post.objects.filter(user=user).order_by('-created_at')[:3]
    print "userfeed count: ",userfeed.count()
    friends = None
    try:
        friends = AllFriends.objects.filter(Q(friends__user=user, status=AllFriends.ACCEPTED)|Q(user=user, status=AllFriends.ACCEPTED)).select_related('user')#.values('user')
    except:
        pass
    template_name = 'vendroid/profile/profile.html'
    company = None
    if profile.type == UserProfile.PROFESSIONAL:
        company = Company.objects.get(userprofile=profile)
        template_name = 'vendroid/profile/professional_profile_V2.html'
    events = CalendarEvent.objects.filter(user=request.user)[:4]
    tasks = Task.objects.filter(user=request.user)[:4]
    picture_wall = pictureWall.objects.filter(user=request.user)
    bids =  Pledge.objects.select_related('product').filter(user=request.user)
    image_url_yelp = None
    name_yelp = None
    description_yelp = None
    name_categories = None
    try:
        """
            Yelp open API call, upon use given srttings
        """
        if profile.yelp_name and profile.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
            location = profile.yelp_location_zip, term = profile.yelp_name, limit = 10,
            sort = YelpClient.SortType.BEST_MATCHED)
            print "result: "
            yelp_rating = result_json
            print 'Yelp: ',yelp_rating
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            name_yelp = yelp_rating['businesses'][0]['name']
            name_categories = yelp_rating['businesses'][0]['categories'][0]
            description_yelp = yelp_rating['businesses'][0]['snippet_text']
    except Exception as e:
        print e
        pass
    context = {
        'user':user,
        'profile':profile,
        'userfeed':userfeed,
        'company':company,
        'professional':profile,
        'friends':friends,
        'events':events,
        'tasks':tasks,
        'picture_wall':picture_wall,
        'bids':bids,
        'pictureWallForm':pictureWallForm(),
        'image_url_yelp':image_url_yelp,
        'name_yelp':name_yelp,
        'description_yelp':description_yelp,
        'name_categories':name_categories,
    }
    return render(request, template_name, context)
from yapjoy_messages.forms import messageForm
@login_required(login_url='/login/')
def public_profile(request, id):
    profile = get_object_or_404(UserProfile, pk=id)
    user = profile.user
    message_success = None
    message_success_text = None
    error_message = None
    form = messageForm()
    userprofile = request.user.userprofile
    if profile == userprofile:
        return HttpResponseRedirect('/profile/')
    userfeed = None
    if profile.type == UserProfile.PROFESSIONAL:
        return HttpResponseRedirect('/professional/profile/%d/'%(profile.id))
    if request.method == "POST":
        user_requested = None
        if 'add_friend' in request.POST:
            add_friend = request.POST.get('add_friend')
            try:
                fr = Friends.objects.get(user=request.user)
                user_requested = AllFriends.objects.create(user_id = add_friend, friends=fr)
            except:
                fr = Friends.objects.create(user=request.user)
                user_requested = AllFriends.objects.create(user_id = add_friend, friends=fr)
            Notifications.objects.create(userprofile=user_requested.user.userprofile, message="You have a friends request from %s"%(request.user.get_full_name()))
            send_email(user_requested.user.email, message="You have a new friend request from %s"%(request.user.get_full_name()), title="New friend request", subject="You have a new friends request on Yapjoy")
        elif 'remove_friend' in request.POST:
            remove_friend = request.POST.get('remove_friend')
            try:
                AllFriends.objects.get(user_id = remove_friend, friends__user_id=request.user).delete()
            except:
                pass
            try:
                AllFriends.objects.get(user_id = request.user.id, friends__user_id=remove_friend).delete()
            except:
                pass
        elif 'messageSend' in request.POST:
            form = messageForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # subject = data['subject']
                message = data['message']
                is_friend_cred = AllFriends.objects.filter(Q(user=user, friends__user=request.user, status=AllFriends.ACCEPTED)|Q(user=request.user, friends__user=user, status=AllFriends.ACCEPTED)|Q(user=request.user, friends__user=user, status=AllFriends.FOLLWOING))
                print "is_friend_cred: ",is_friend_cred
                if userprofile.subscribed and userprofile.amount > 0 or is_friend_cred:
                    Message.objects.create(sender=request.user, receiver=user, message=message)
                    message_success = "Your message has been successfully sent."
                    if not is_friend_cred:
                        userprofile.amount -= 1
                        userprofile.save()
                else:
                    if not userprofile.subscribed:
                        message_success = "You are not subscribed."
                    elif userprofile.amount <= 0:
                        message_success = "You donot have sufficient credit. Kindly subscribe again."
            else:
                print "message form is in valid"
        elif "invite_user" in request.POST:
            print 'Inviting User'
            try:
                code_sub = SubscriptionCode.objects.get_or_create(user=user)[0].code
                send_email(sendTo=user.email, message="You have been invited by %s to join YapJoy. Click on the following link below to setup your profile.<br /><br /><a href='http://www.yapjoy.com/registration/wizard/%s'>View Invitation</a>"%(request.user.get_full_name(), code_sub), title="Invitation by %s to YapJoy"%(request.user.get_full_name()), subject="Invitation by %s to YapJoy"%(request.user.get_full_name()))
                message_success_text = "You have successfully invited %s"%(user.get_full_name())
            except:
                pass

        else:
            postText = request.POST.get('Post_comment')
            images = request.FILES.get('image')
            if images:
                Post.objects.create(user=request.user,user_wall=user, text=postText, image=images)
            else:
                if AllFriends.objects.filter(Q(user=user, friends__user=request.user, status=AllFriends.ACCEPTED)|Q(user=request.user, friends__user=user, status=AllFriends.ACCEPTED)).count() > 0:
                    Post.objects.create(user=request.user,user_wall=user, text=postText)
                else:
                    error_message = "You can only post on your friends wall."
    if request.user.userprofile.type == UserProfile.PROFESSIONAL:
        userfeed = None
    else:
        prof = request.user.userprofile
        friend = AllFriends.objects.filter(Q(friends__user=request.user, user=user, status=AllFriends.ACCEPTED)|Q(friends__user=user, user=request.user, status=AllFriends.ACCEPTED))
        if friend:
            userfeed = Post.objects.filter(user_wall=user).order_by('-created_at')
    # is_friend_cred = AllFriends.objects.filter(Q(user=user, friends__user=request.user, status=AllFriends.ACCEPTED)|Q(user=request.user, friends__user=user, status=AllFriends.ACCEPTED)|Q(user=request.user, friends__user=user, status=AllFriends.FOLLWOING))
    # print "is_friend_cred: ",is_friend_cred
    is_friend = False
    is_friend_sent = False
    try:
        is_friend = AllFriends.objects.filter(Q(friends__user=user, user=request.user, status=AllFriends.ACCEPTED)|Q(user=user, friends__user=request.user, status=AllFriends.ACCEPTED)|Q(user=user, friends__user=request.user, status=AllFriends.FOLLWOING))#.filter(status=AllFriends.FRIEND)
        is_friend_sent = AllFriends.objects.filter(Q(friends__user=user, user=request.user)|Q(user=user, friends__user=request.user))#.filter(status=AllFriends.FRIEND)
        # if is_friend.filter(status=AllFriends.ACCEPTED).count() == 0:
        #     is_friend = None
    except:
        pass
    friends = None
    tasks = None
    events = None
    if is_friend:
        try:
            if is_friend.filter(status=AllFriends.ACCEPTED).count()>0 or is_friend.filter(status=AllFriends.FOLLWOING).count()>0:
                friends = AllFriends.objects.filter(Q(user=user)|Q(friends__user=user)).select_related('user')
                print 'friends: ',friends
                userREQ = []
                userREQ.append(request.user)
                tasks = Task.objects.filter(assign__in=userREQ, user=user)
                print tasks
                events = CalendarEvent.objects.filter(assign_event_users__in=userREQ, user=user)
                print events
                # userfeed = Post.objects.filter(Q(user=user)|Q(user_wall=user, user=request.user)).order_by('-created_at')

        except Exception as e:
            print e
            pass
    products = Product.objects.filter(user=user).select_related('user').order_by('amount')
    print "User Feed: ",userfeed
    context = {
        'user':user,
        'profile':profile,
        'userfeed':userfeed,
        'tasks':tasks,
        'events':events,
        'friends':friends,
        'userprofile':userprofile,
        'is_friend':is_friend,
        'is_friend_sent':is_friend_sent,
        'products':products,
        'form':form,
        'message_success':message_success,
        'message_success_text':message_success_text,
        'error_message':error_message,
    }
    return render(request, 'vendroid/profile/public_profile.html',context)




@login_required(login_url='/login/')
def settings_view(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.PROFESSIONAL:
        return HttpResponseRedirect('/company/settings/')
    initial = {
        'email':user.email,

    }
    initial_profile = {
        'first_name':user.first_name,
        'last_name':user.last_name,
        'age':profile.age,
        'gender':profile.gender,
        'wedding_date':profile.wedding_date,
        'street':profile.street,
        'city':profile.city,
        'state':profile.state,
        'zip':profile.zip,
        'looking_for':profile.looking_for,
        'image':profile.image,
        'cover_image':profile.cover_image,
        'wedding_location':profile.wedding_location,
        'budget':profile.budget,
    }
    initialPrivacy = {
        'notification_events':profile.notification_events,
        'notification_tasks':profile.notification_tasks,
    }
    profileform = profileForm(initial=initial_profile)
    emailform = emailEditForm(initial=initial)
    privacyform = privacy(initial=initialPrivacy)
    passwordform = passwordForm()
    emailformSubmit = None
    looking_for_error = ""
    successMessage = None
    privacyformSubmit = None
    if "notification_sig" in request.POST:
        print "notification_events"
        privacyform = privacy(request.POST)
        if privacyform.is_valid():
            data = privacyform.cleaned_data
            notification_events = data['notification_events']
            notification_tasks = data['notification_tasks']
            profile.notification_events = notification_events
            profile.notification_tasks = notification_tasks
            profile.save()
            successMessage = 'Privacy settings changed successfully.'
        privacyformSubmit = "True"
    if request.method == 'POST':
        if 'emailformSignal' in request.POST:
            emailform = emailEditForm(request.POST)
            if emailform.is_valid():
                data = emailform.cleaned_data
                email = data['email']
                print email
                user.email = email
                user.username = email
                user.save()
                print 'working well'
                successMessage = 'Email changed successfully.'
            emailformSubmit = "True"


        if 'passwordformSignal' in request.POST:
            passwordform = passwordForm(request.POST)
            if passwordform.is_valid():
                data = passwordform.cleaned_data
                password = data['password']
                user.set_password(password)
                user.save()
                print 'password submitted'
                successMessage = 'Password changed successfully.'
            emailformSubmit = "True"
        if 'profileform' in request.POST:
            profileform = profileForm(request.POST, request.FILES)
            if profileform.is_valid():
                data = profileform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                gender = data['gender']
                age = data['age']
                wedding_date = data['wedding_date']
                wedding_location = data['wedding_location']
                budget = data['budget']
                print wedding_location, budget
                profile.wedding_location = wedding_location
                profile.budget = budget
                # profile.save()
                if wedding_date:
                    print 'inside wedding_date part'
                    try:
                        wed_cal = CalendarEvent.objects.get(user=user, is_wedding=True)
                        wed_cal.start = wedding_date
                        wed_cal.end = wedding_date
                        wed_cal.save()
                    except Exception as e:
                        print e
                        CalendarEvent.objects.create(title="Wedding Day", user=user, is_wedding=True, start=wedding_date, end=wedding_date, all_day=True)
                street = data['street']
                city = data['city']
                state = data['state']
                zip = data['zip']
                image = data['image']
                # cover_image = data['cover_image']
                looking_for = data['looking_for']
                print 'looking for: ',looking_for
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                profile.gender = gender
                profile.wedding_date = wedding_date
                profile.street = street
                profile.city = city
                profile.state = state
                profile.zip = zip
                profile.age = age

                if not image == UserProfile.DEFAULT_IMAGE and image:
                    print 'image is: ',image
                    profile.image = image
                    profile.save()
                # if not cover_image == UserProfile.DEFAULT_COVER_IMAGE and cover_image:
                #     profile.cover_image = cover_image
                assigned_to = request.POST.getlist('assigned_to')
                if assigned_to:
                    optionsSearch_users.objects.filter(userprofile = profile).delete()
                    print assigned_to
                    looking_for_string = ""
                    for o in assigned_to:
                        os = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                        looking_for_string += "%s "%(os.open_search.name)
                    profile.looking_for = looking_for_string
                else:
                    looking_for_error = "Atleast one looking for is required."
                print "Looking for: ",profile.looking_for
                profile.save()
                print profile.budget, profile.wedding_location
                # try:
                #     CalendarEvent.objects.get(user=user, title='Wedding Day')
                # except:
                #     CalendarEvent.objects.create(user=user, title='Wedding Day', start=wedding_date, end=wedding_date, all_day=True)
                successMessage = 'Profile edited successfully.'

    looking_for = optionsSearch.objects.all()
    looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search')
    if looking_for_selected:
        looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search'))
    context = {
        'emailform':emailform,
        'emailformSubmit':emailformSubmit,
        'successMessage':successMessage,
        'passwordform':passwordform,
        'profileform':profileform,
        'profile':profile,
        'looking_for_selected':looking_for_selected,
        'looking_for':looking_for,
        'privacyform':privacyform,
        'privacyformSubmit':privacyformSubmit,
        'looking_for_error':looking_for_error,
    }
    return render(request, 'vendroid/iFrame/settings.html', context)\




@login_required(login_url='/login/')
def settings_view_v2(request):
    user = request.user
    profile = user.userprofile
    # if profile.type == UserProfile.PROFESSIONAL:
    #     return HttpResponseRedirect('/company/settings/')
    initial = {
        'email':user.email,

    }
    initial_profile = {
        'first_name':user.first_name,
        'last_name':user.last_name,
        'age':profile.age,
        'gender':profile.gender,
        'wedding_date':profile.wedding_date,
        'street':profile.street,
        'city':profile.city,
        'state':profile.state,
        'zip':profile.zip,
        'looking_for':profile.looking_for,
        'image':profile.image,
        'cover_image':profile.cover_image,
        'wedding_location':profile.wedding_location,
        'budget':profile.budget,
    }
    initialPrivacy = {
        'notification_events':profile.notification_events,
        'notification_tasks':profile.notification_tasks,
    }
    profileform = profileForm(initial=initial_profile)
    emailform = emailEditForm(initial=initial)
    privacyform = privacy(initial=initialPrivacy)
    passwordform = passwordForm()
    emailformSubmit = None
    looking_for_error = ""
    successMessage = None
    privacyformSubmit = None
    if "notification_sig" in request.POST:
        print "notification_events"
        privacyform = privacy(request.POST)
        if privacyform.is_valid():
            data = privacyform.cleaned_data
            notification_events = data['notification_events']
            notification_tasks = data['notification_tasks']
            profile.notification_events = notification_events
            profile.notification_tasks = notification_tasks
            profile.save()
            successMessage = 'Privacy settings changed successfully.'
        privacyformSubmit = "True"
    if request.method == 'POST':
        if 'emailformSignal' in request.POST:
            emailform = emailEditForm(request.POST)
            if emailform.is_valid():
                data = emailform.cleaned_data
                email = data['email']
                print email
                user.email = email
                user.username = email
                user.save()
                print 'working well'
                successMessage = 'Email changed successfully.'
            emailformSubmit = "True"


        if 'passwordformSignal' in request.POST:
            passwordform = passwordForm(request.POST)
            if passwordform.is_valid():
                data = passwordform.cleaned_data
                password = data['password']
                user.set_password(password)
                user.save()
                print 'password submitted'
                successMessage = 'Password changed successfully.'
            emailformSubmit = "True"
        if 'profileform' in request.POST:
            profileform = profileForm(request.POST, request.FILES)
            if profileform.is_valid():
                data = profileform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                gender = data['gender']
                age = data['age']
                wedding_date = data['wedding_date']
                wedding_location = data['wedding_location']
                budget = data['budget']
                print wedding_location, budget
                profile.wedding_location = wedding_location
                profile.budget = budget
                # profile.save()
                if wedding_date:
                    print 'inside wedding_date part'
                    try:
                        wed_cal = CalendarEvent.objects.get(user=user, is_wedding=True)
                        wed_cal.start = wedding_date
                        wed_cal.end = wedding_date
                        wed_cal.save()
                    except Exception as e:
                        print e
                        CalendarEvent.objects.create(title="Wedding Day", user=user, is_wedding=True, start=wedding_date, end=wedding_date, all_day=True)
                street = data['street']
                city = data['city']
                state = data['state']
                zip = data['zip']
                image = data['image']
                # cover_image = data['cover_image']
                looking_for = data['looking_for']
                print 'looking for: ',looking_for
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                profile.gender = gender
                profile.wedding_date = wedding_date
                profile.street = street
                profile.city = city
                profile.state = state
                profile.zip = zip
                profile.age = age

                if not image == UserProfile.DEFAULT_IMAGE and image:
                    print 'image is: ',image
                    profile.image = image
                    profile.save()
                # if not cover_image == UserProfile.DEFAULT_COVER_IMAGE and cover_image:
                #     profile.cover_image = cover_image
                assigned_to = request.POST.getlist('assigned_to')
                if assigned_to:
                    optionsSearch_users.objects.filter(userprofile = profile).delete()
                    print assigned_to
                    looking_for_string = ""
                    for o in assigned_to:
                        os = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                        looking_for_string += "%s "%(os.open_search.name)
                    profile.looking_for = looking_for_string
                else:
                    looking_for_error = "Atleast one looking for is required."
                print "Looking for: ",profile.looking_for
                profile.save()
                print profile.budget, profile.wedding_location
                # try:
                #     CalendarEvent.objects.get(user=user, title='Wedding Day')
                # except:
                #     CalendarEvent.objects.create(user=user, title='Wedding Day', start=wedding_date, end=wedding_date, all_day=True)
                successMessage = 'Profile edited successfully.'
            else:
                print profileform.errors
    looking_for = optionsSearch.objects.all()
    looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search')
    if looking_for_selected:
        looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search'))
    context = {
        'emailform':emailform,
        'emailformSubmit':emailformSubmit,
        'successMessage':successMessage,
        'passwordform':passwordform,
        'profileform':profileform,
        'profile':profile,
        'looking_for_selected':looking_for_selected,
        'looking_for':looking_for,
        'privacyform':privacyform,
        'privacyformSubmit':privacyformSubmit,
        'looking_for_error':looking_for_error,
        # 'id':id,
    }
    return render(request, 'vendroid/iFrame/settingsv2.html', context)\




@login_required(login_url='/login/')
def settings_delete(request):
    user = request.user
    error_message = None
    form = DeleteConfirmForm()
    if request.method == "POST":
        form = DeleteConfirmForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            password = data['password']
            password_check = user.check_password(password)
            if password_check:
                user.is_active = False
                user.save()
                return HttpResponseRedirect('/logout/')
                # user.email = "yapjoy_user_delete_%s"%(str(user.id))
                print 'delete user here'
                print "delete the account ehre"
            else:
                error_message = "Password is not a valid password, Try again."
            print password_check
            print password
    context = {
        'form':form,
        'error_message':error_message,
    }
    return render(request, 'vendroid/settings/account_remove.html', context)

@login_required(login_url='/login/')
def settings_viewV2(request):
    user = request.user
    profile = user.userprofile
    if profile.type == UserProfile.PROFESSIONAL:
        return HttpResponseRedirect('/company/settings/')
    initial = {
        'email':user.email,

    }
    initial_profile = {
        'first_name':user.first_name,
        'last_name':user.last_name,
        'age':profile.age,
        'gender':profile.gender,
        'wedding_date':profile.wedding_date,
        'street':profile.street,
        'city':profile.city,
        'state':profile.state,
        'zip':profile.zip,
        'looking_for':profile.looking_for,
        'image':profile.image,
        'cover_image':profile.cover_image,
    }
    initialPrivacy = {
        'notification_events':profile.notification_events,
        'notification_tasks':profile.notification_tasks,
    }
    profileform = profileForm(initial=initial_profile)
    emailform = emailEditForm(initial=initial)
    privacyform = privacy(initial=initialPrivacy)
    passwordform = passwordForm()
    emailformSubmit = None
    successMessage = None
    privacyformSubmit = None
    if "notification_sig" in request.POST:
        print "notification_events"
        privacyform = privacy(request.POST)
        if privacyform.is_valid():
            data = privacyform.cleaned_data
            notification_events = data['notification_events']
            notification_tasks = data['notification_tasks']
            profile.notification_events = notification_events
            profile.notification_tasks = notification_tasks
            profile.save()
            successMessage = 'Privacy settings changed successfully.'
        privacyformSubmit = "True"
    if request.method == 'POST':
        if 'emailformSignal' in request.POST:
            emailform = emailEditForm(request.POST)
            if emailform.is_valid():
                data = emailform.cleaned_data
                email = data['email']
                print email
                user.email = email
                user.username = email
                user.save()
                print 'working well'
                successMessage = 'Email changed successfully.'
            emailformSubmit = "True"


        if 'passwordformSignal' in request.POST:
            passwordform = passwordForm(request.POST)
            if passwordform.is_valid():
                data = passwordform.cleaned_data
                password = data['password']
                user.set_password(password)
                user.save()
                print 'password submitted'
                successMessage = 'Password changed successfully.'
            emailformSubmit = "True"
        if 'profileform' in request.POST:
            profileform = profileForm(request.POST, request.FILES)
            if profileform.is_valid():
                data = profileform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                gender = data['gender']
                age = data['age']
                wedding_date = data['wedding_date']
                if wedding_date:
                    print 'inside wedding_date part'
                    try:
                        wed_cal = CalendarEvent.objects.get(user=user, is_wedding=True)
                        wed_cal.start = wedding_date
                        wed_cal.end = wedding_date
                        wed_cal.save()
                    except Exception as e:
                        print e
                        CalendarEvent.objects.create(title="Wedding Day", user=user, is_wedding=True, start=wedding_date, end=wedding_date, all_day=True)
                street = data['street']
                city = data['city']
                state = data['state']
                zip = data['zip']
                image = data['image']
                cover_image = data['cover_image']
                looking_for = data['looking_for']
                print 'looking for: ',looking_for
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                profile.gender = gender
                profile.wedding_date = wedding_date
                profile.street = street
                profile.city = city
                profile.state = state
                profile.zip = zip
                profile.age = age
                if not image == UserProfile.DEFAULT_IMAGE and image:
                    print 'image is: ',image
                    profile.image = image
                if not cover_image == UserProfile.DEFAULT_COVER_IMAGE and cover_image:
                    profile.cover_image = cover_image
                assigned_to = request.POST.getlist('assigned_to')
                if assigned_to:
                    optionsSearch_users.objects.filter(userprofile = profile).delete()
                    print assigned_to
                    looking_for_string = ""
                    for o in assigned_to:
                        os = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                        looking_for_string += "%s "%(os.open_search.name)
                    profile.looking_for = looking_for_string
                print "Looking for: ",profile.looking_for
                profile.save()
                # try:
                #     CalendarEvent.objects.get(user=user, title='Wedding Day')
                # except:
                #     CalendarEvent.objects.create(user=user, title='Wedding Day', start=wedding_date, end=wedding_date, all_day=True)
                successMessage = 'Profile edited successfully.'

    looking_for = optionsSearch.objects.all()
    looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search')
    if looking_for_selected:
        looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search'))
    context = {
        'emailform':emailform,
        'emailformSubmit':emailformSubmit,
        'successMessage':successMessage,
        'passwordform':passwordform,
        'profileform':profileform,
        'profile':profile,
        'looking_for_selected':looking_for_selected,
        'looking_for':looking_for,
        'privacyform':privacyform,
        'privacyformSubmit':privacyformSubmit,
    }
    return render(request, 'vendroid/iFrame/settings.html', context)

from yapjoy_yelpclient.client import *
@login_required(login_url='/login/')
def company_settings_view(request):
    user = request.user
    profile = user.userprofile

    initial = {
        'email':user.email,

    }
    company = get_object_or_404(Company, userprofile=profile)
    print company
    emailform = emailEditForm(initial=initial)
    initial_company = {
        'name':company.name,
        'description':company.description,
        'payment_terms':company.payment_terms,
        'employees':company.employees,
        'street':profile.street,
        'city':profile.city,
        'state':profile.state,
        'zip':profile.zip,
        'phone':profile.phone,
    }
    initialPrivacy = {
        'notification_events':profile.notification_events,
        'notification_tasks':profile.notification_tasks,
    }
    privacyform = privacy(initial=initialPrivacy)
    company_form = companySettingsForm(initial=initial_company)
    initial_yelp = {}
    if profile.yelp_name and profile.yelp_location_zip:
        initial_yelp = {
            'yelp_name':profile.yelp_name,
            'yelp_location_zip':profile.yelp_location_zip,
        }
    yelp_form = yelpForm(initial=initial_yelp)
    initial_profile = {
        'first_name':user.first_name,
        'last_name':user.last_name,
        'age':profile.age,
        'gender':profile.gender,
        'looking_for':profile.looking_for,
        'image':profile.image,
        'cover_image':profile.cover_image,
    }

    profileform = profileProfessionalForm(initial=initial_profile)

    passwordform = passwordForm()
    emailformSubmit = None
    companyFormSubmit = None
    yelpFormSubmit = None
    successMessage = None
    privacyformSubmit = None
    looking_for_error = ""
    if "notification_sig" in request.POST:
        print "notification_events"
        privacyform = privacy(request.POST)
        if privacyform.is_valid():
            data = privacyform.cleaned_data
            notification_events = data['notification_events']
            notification_tasks = data['notification_tasks']
            profile.notification_events = notification_events
            profile.notification_tasks = notification_tasks
            profile.save()
            successMessage = 'Privacy settings changed successfully.'
        privacyformSubmit = "True"
    if request.method == 'POST':
        if 'emailformSignal' in request.POST:
            emailform = emailEditForm(request.POST)
            if emailform.is_valid():
                data = emailform.cleaned_data
                email = data['email']
                user.email = email
                user.save()
                print 'working well'
                successMessage = 'Email changed successfully.'
            emailformSubmit = "True"


        elif 'passwordformSignal' in request.POST:
            passwordform = passwordForm(request.POST)
            if passwordform.is_valid():
                data = passwordform.cleaned_data
                password = data['password']
                user.set_password(password)
                user.save()
                print 'password submitted'
                successMessage = 'Password changed successfully.'
            emailformSubmit = "True"
        elif 'profileform' in request.POST:
            profileform = profileProfessionalForm(request.POST, request.FILES)
            if profileform.is_valid():
                data = profileform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                gender = data['gender']
                age = data['age']
                image = data['image']
                cover_image = data['cover_image']
                looking_for = data['looking_for']
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                profile.gender = gender
                profile.age = age
                # profile.looking_for = looking_for
                assigned_to = request.POST.getlist('assigned_to')
                if assigned_to:
                    optionsSearch_users.objects.filter(userprofile = profile).delete()
                    print assigned_to
                    looking_for_string = ""
                    for o in assigned_to:
                        osp = optionsSearch_users.objects.create(userprofile=profile, open_search_id=int(o))
                        looking_for_string += "%s "%(osp.open_search.name)
                    profile.looking_for = looking_for_string
                elif not assigned_to:
                    looking_for_error = "Atleast one looking for is required."
                if not image == UserProfile.DEFAULT_IMAGE and image:
                    print 'image is: ',image
                    profile.image = image
                if not cover_image == UserProfile.DEFAULT_COVER_IMAGE and cover_image:
                    profile.cover_image = cover_image
                profile.save()
                successMessage = 'Profile edited successfully.'
        elif 'companyForm_tag' in request.POST:
            company_form = companySettingsForm(request.POST)
            if company_form.is_valid():
                data = company_form.cleaned_data
                name = data['name']
                description = data['description']
                payment_terms = data['payment_terms']
                employees = data['employees']
                street = data['street']
                city = data['city']
                state = data['state']
                zip = data['zip']
                phone = data['phone']
                company.name = name
                company.description = description
                company.payment_terms = payment_terms
                company.employees = employees
                company.save()
                profile.street = street
                profile.city = city
                profile.state = state
                profile.zip = zip
                profile.phone = phone
                profile.save()
                successMessage = "Company details are sucessfully added."
            companyFormSubmit = "Form Submitted"
        elif "yelpForm_tag" in request.POST:
            yelp_form = yelpForm(request.POST)
            if yelp_form.is_valid():
                data = yelp_form.cleaned_data
                # 'yelp_location_zip','yelp_name'
                yelp_location_zip = data['yelp_location_zip']
                yelp_name = data['yelp_name']
                profile.yelp_location_zip = yelp_location_zip
                profile.yelp_name = yelp_name
                profile.save()
                successMessage = "Yelp details are sucessfully added."
            yelpFormSubmit = True
    result_json = None
    image_url_yelp = None
    name_yelp = None
    name_categories = None
    description_yelp = None
    try:
        """
            Yelp open API call, upon use given srttings
        """
        if profile.yelp_name and profile.yelp_location_zip:
            client = YelpClient(keys_yelp)
            result_json = client.search_by_location(
            location = profile.yelp_location_zip, term = profile.yelp_name, limit = 10,
            sort = YelpClient.SortType.BEST_MATCHED)
            print "result: "
            yelp_rating = result_json
            print 'Yelp: ',yelp_rating
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url']
            image_url_yelp = yelp_rating['businesses'][0]['rating_img_url_large']
            name_yelp = yelp_rating['businesses'][0]['name']
            name_categories = yelp_rating['businesses'][0]['categories'][0]
            description_yelp = yelp_rating['businesses'][0]['snippet_text']
    except Exception as e:
        print e
        pass
    looking_for = optionsSearch.objects.all()
    looking_for_selected = optionsSearch_users.objects.filter(userprofile = profile).select_related('open_search')
    print 'looking for: ', looking_for
    print 'looking for selected: ', looking_for_selected
    if looking_for_selected:
        looking_for = looking_for.exclude(id__in=looking_for_selected.values('open_search'))
    print 'looking for: ', looking_for
    print 'looking for selected: ', looking_for_selected
    context = {
        'emailform':emailform,
        'emailformSubmit':emailformSubmit,
        'companyFormSubmit':companyFormSubmit,
        'yelpFormSubmit':yelpFormSubmit,
        'successMessage':successMessage,
        'passwordform':passwordform,
        'profileform':profileform,
        'profile':profile,
        'company_form':company_form,
        'yelp_form':yelp_form,
        'looking_for':looking_for,
        'looking_for_selected':looking_for_selected,
        'privacyform':privacyform,
        'privacyformSubmit':privacyformSubmit,
        'result_json':result_json,
        'image_url_yelp':image_url_yelp,
        'name_yelp':name_yelp,
        'description_yelp':description_yelp,
        'name_categories':name_categories,
        'looking_for_error':looking_for_error,
    }
    return render(request, 'vendroid/iFrame/company_settings.html', context)

def activate(request, code):
    try:
        profile = UserProfile.objects.select_related('user').get(activation_id=code)
        user = profile.user
        user.is_active = True
        user.save()
        return HttpResponseRedirect('/login/')

    except:
        raise Http404

def forgotPassword(request):
    success_message = None
    form = PasswordResetForm()
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            user = get_object_or_404(User, email__iexact=email)
            pr = PasswordRecover.objects.create(user=user)
            message = "<p class='text-center'>Click the following link to recover your password.</p><br /><br /><a class='btn btn-primary btn-block' href='http://www.yapjoy.com/reset_password/%s/' target='_blank'>Reset Now</a>"%(pr.code)
            send_email(sendTo=email, message=message, title='Dear %s, <br /><br />You or someone pretending to be you have requested a password reset.'%(user.get_full_name()), subject="Password Reset - YapJoy")
            success_message = "Email has been sent to the following email address: %s, Check your email."%(email)
    context = {
        'form':form,
        'success_message':success_message,
    }
    return render(request, 'vendroid/registration/forgot_password.html', context)

def ResetPassword(request, code):
    pr = get_object_or_404(PasswordRecover, code=code, is_recovered=False)
    success_message = None
    error_message = None
    form = Passowrd_reset_form()
    if request.method == "POST":
        form = Passowrd_reset_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            if not email == pr.user.email:
                error_message = 'Enter a valid email address.'
            elif email == pr.user.email:
                user = pr.user
                user.set_password(password)
                user.is_active = True
                user.save()
                pr.is_recovered = True
                pr.save()

                success_message = "Your password has been successfully changed."
        else:
            print 'form is invalid: '
    context = {
        'form':form,
        'success_message':success_message,
        'error_message':error_message,
        'code':code,
    }
    return render(request, 'vendroid/registration/recover_password.html', context)

def landing(request):
    return render(request, 'vendroid/home/home.html')

@csrf_exempt
def login(request):
    form=loginForm()
    registerform=NewRegForm()
    InvalidDetails = None
    if request.method== 'POST':
        if 'confirm_password' in request.POST:
            registerform=NewRegForm(request.POST)
            if registerform.is_valid():
                data = registerform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                email = data['email']
                password = data['password']
                type = data['type']
                user = User.objects.create(email=email, username=email, first_name=first_name, last_name=last_name)
                user.set_password(password)
                user.save()
                profile = user.userprofile
                profile.type = type
                profile.save()
                # if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
                #     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Videography',user=user,status=Product.PENDING)
                if type == UserProfile.PROFESSIONAL:
                    company = Company.objects.create(userprofile=profile)
                try:
                    message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                    send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                except Exception as e:
                    print e
                #     print "email not sent"
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                # if type == UserProfile.BRIDE or type == UserProfile.GROOM:
                #     sub = SubscriptionCode.objects.create(user=user, code=id_generator())
                #     return HttpResponseRedirect('/subscribtion_wizard/%s'%(sub.code))
                auth_login(request, user)
                print 'auth'
                return HttpResponseRedirect('/')
        else:
            form = loginForm(request.POST)
            print 'here'

            if form.is_valid():
                print '2'
                data = form.cleaned_data
                username = data['username']
                password = data['password']
                print 'redirect: ', username, password
                user_auth = authenticate(username=username, password=password)
                # if user_auth.is_active == False:
                #     InvalidDetails = "User is not activated."
                #     return render(request, 'login.html',{
                #      'form':form,
                #     'InvalidDetails':InvalidDetails,
                #     })
                try:
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
                        print 'auth'
                        return HttpResponseRedirect('/')
                    else:
                        InvalidDetails = "This account has been deavtivated."
                except Exception as e:
                    print e
                    InvalidDetails = "The username and/or password you entered is incorrect"
            else:
                InvalidDetails = "Please Enter Details Correctly"

    return render(request, 'vendroid/home/home.html',{
                 'form':form,
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                })

@csrf_exempt
def loginv2(request):
    form=loginForm()
    registerform=NewRegForm2()
    InvalidDetails = None
    if request.method== 'POST':
        if 'register' in request.POST:
            registerform=NewRegForm2(request.POST)
            if registerform.is_valid():
                data = registerform.cleaned_data
                # first_name = data['first_name']
                # last_name = data['last_name']
                email = data['email']
                password = data['password']
                # type = data['type']
                user = User.objects.create(email=email, username=email
                                           # , first_name=first_name, last_name=last_name
                                           )
                user.set_password(password)
                user.save()
                profile = user.userprofile
                # profile.type = type
                profile.save()
                # if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
                #     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Videography',user=user,status=Product.PENDING)
                # if type == UserProfile.PROFESSIONAL:
                #     company = Company.objects.create(userprofile=profile)
                # try:
                #     message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                #     send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                # except Exception as e:
                #     print e
                #     print "email not sent"
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                # if type == UserProfile.BRIDE or type == UserProfile.GROOM:
                #     sub = SubscriptionCode.objects.create(user=user, code=id_generator())
                #     return HttpResponseRedirect('/subscribtion_wizard/%s'%(sub.code))
                auth_login(request, user)
                print 'auth'
                return HttpResponseRedirect('/demov2/select/')
        else:
            form = loginForm(request.POST)
            print 'here'

            if form.is_valid():
                print '2'
                data = form.cleaned_data
                username = data['username']
                password = data['password']
                print 'redirect: ', username, password
                user_auth = authenticate(username=username, password=password)
                # if user_auth.is_active == False:
                #     InvalidDetails = "User is not activated."
                #     return render(request, 'login.html',{
                #      'form':form,
                #     'InvalidDetails':InvalidDetails,
                #     })
                try:
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
                        print 'auth'
                        return HttpResponseRedirect('/demov2/select/')
                    else:
                        InvalidDetails = "This account has been deavtivated."
                except Exception as e:
                    print e
                    InvalidDetails = "The username and/or password you entered is incorrect"
            else:
                InvalidDetails = "Please Enter Details Correctly"

    return render(request, 'moments/home.html',{
                 'form':form,
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                })
from django.views.decorators.cache import cache_control
from  django.views.decorators.gzip import gzip_page
# @gzip_page
@cache_control(private=True)
@csrf_exempt
def loginv3(request):
    form=loginForm()
    pre_register = request.GET.get('pre_register')
    request_success_form = False
    registerform=NewRegForm2()
    req_form = RegisterRequestForm()
    InvalidDetails = None
    InvalidDetailsReg = None
    if request.method== 'POST':
        if 'register' in request.POST:
            registerform=NewRegForm2(request.POST)
            if registerform.is_valid():
                data = registerform.cleaned_data
                # first_name = data['first_name']
                # last_name = data['last_name']
                email = data['email']
                password = data['password']
                # type = data['type']
                user = User.objects.create(email=email, username=email
                                           # , first_name=first_name, last_name=last_name
                                           )
                user.set_password(password)
                user.save()
                profile = user.userprofile
                # profile.type = type
                profile.save()
                # if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
                #     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Videography',user=user,status=Product.PENDING)
                # if type == UserProfile.PROFESSIONAL:
                #     company = Company.objects.create(userprofile=profile)
                # try:
                #     message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                #     send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                # except Exception as e:
                #     print e
                #     print "email not sent"
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                # if type == UserProfile.BRIDE or type == UserProfile.GROOM:
                #     sub = SubscriptionCode.objects.create(user=user, code=id_generator())
                #     return HttpResponseRedirect('/subscribtion_wizard/%s'%(sub.code))
                auth_login(request, user)
                print 'auth: ',
                return HttpResponseRedirect('/select/')
        elif 'requester' in request.POST:
            req_form = RegisterRequestForm(request.POST)
            if req_form.is_valid():
                req_form.save()
                req_form = RegisterRequestForm()
                request_success_form = True

        else:
            form = loginForm(request.POST)
            print 'here'

            if form.is_valid():
                print '2'
                data = form.cleaned_data
                username = data['username']
                password = data['password']
                print 'redirect: ', username, password
                user_auth = authenticate(username=username, password=password)
                # if user_auth.is_active == False:
                #     InvalidDetails = "User is not activated."
                #     return render(request, 'login.html',{
                #      'form':form,
                #     'InvalidDetails':InvalidDetails,
                #     })
                try:
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
                        print 'auth'
                        products = Product.objects.filter(user_id=user_auth.id)
                        # print 'products: ', products, products.count()
                        if products:
                            return HttpResponseRedirect('/')
                        return HttpResponseRedirect('/select/')
                    else:
                        InvalidDetails = "This account has been deavtivated."
                except Exception as e:
                    print e
                    InvalidDetails = "The username and/or password you entered is incorrect"
            else:
                InvalidDetails = "Please enter correct details"
    print 'req form'
    # import pusher
    #
    # pusher_client = pusher.Pusher(
    #     app_id='267805',
    #     key='896f67f3b91c49de3343',
    #     secret='6b7bd633bfad598c145b',
    #     # ssl=True
    # )
    #
    # pusher_client.trigger('test_channel', 'my_event', {'message': 'hello world'})
    return render(request, 'moments/homev3.html',{
                 'form':form,
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                 'req_form':req_form,
                 'pre_register':pre_register,
                 'request_success_form':request_success_form,
                })

@login_required(login_url='/login/')
def redirect_view_select(request):
    return HttpResponseRedirect('/crm/invoices/bulk/create/')

from yapjoy_teamschat.models import EventTeam
@cache_control(private=True)
@csrf_exempt
def loginv3pre(request):
    form=loginForm()
    pre_register = False
    request_success_form = False
    registerform=NewRegForm2()
    req_form = RegisterRequestForm()
    InvalidDetails = None
    InvalidDetailsReg = None
    # if request.method== 'POST':
        # if 'register' in request.POST:
        #     registerform=NewRegForm2(request.POST)
        #     if registerform.is_valid():
        #         data = registerform.cleaned_data
        #         # first_name = data['first_name']
        #         # last_name = data['last_name']
        #         email = data['email']
        #         password = data['password']
        #         # type = data['type']
        #         user = User.objects.create(email=email, username=email
        #                                    # , first_name=first_name, last_name=last_name
        #                                    )
        #         user.set_password(password)
        #         user.save()
        #         profile = user.userprofile
        #         # profile.type = type
        #         profile.save()
        #         # if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
        #         #     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
        #         #     Product.objects.create(title='Videography',user=user,status=Product.PENDING)
        #         # if type == UserProfile.PROFESSIONAL:
        #         #     company = Company.objects.create(userprofile=profile)
        #         # try:
        #         #     message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
        #         #     send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
        #         # except Exception as e:
        #         #     print e
        #         #     print "email not sent"
        #         user.backend = 'django.contrib.auth.backends.ModelBackend'
        #         # if type == UserProfile.BRIDE or type == UserProfile.GROOM:
        #         #     sub = SubscriptionCode.objects.create(user=user, code=id_generator())
        #         #     return HttpResponseRedirect('/subscribtion_wizard/%s'%(sub.code))
        #         auth_login(request, user)
        #         print 'auth'
        #         return HttpResponseRedirect('/select/')
        # elif 'requester' in request.POST:
        #     pass
        #     # req_form = RegisterRequestForm(request.POST)
        #     # if req_form.is_valid():
        #     #     req_form.save()
        #     #     req_form = RegisterRequestForm()
        #     #     request_success_form = True

        # else:
    if request.method == "POST":
        form = loginForm(request.POST)
        print 'here'

        if form.is_valid():
            print '2'
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            print 'redirect: ', username, password
            user_auth = authenticate(username=username, password=password)
            # if user_auth.is_active == False:
            #     InvalidDetails = "User is not activated."
            #     return render(request, 'login.html',{
            #      'form':form,
            #     'InvalidDetails':InvalidDetails,
            #     })
            try:
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
                    print 'auth'
                    # products = Product.objects.filter(user_id=user_auth.id)
                    # # print 'products: ', products, products.count()
                    # events = EventTeam.objects.filter(Q(user_id=user_auth.id)|Q(friends__contains=user_auth.id))
                    # if EventTeam.objects.filter(Q(user_id=user_auth.id)) or EventTeam.friends.filter(id__in=user_auth.id):
                    return HttpResponseRedirect('/bg/profile/')
                    # return HttpResponseRedirect('/bg/event/create/')
                else:
                    InvalidDetails = "This account has been deavtivated."
            except Exception as e:
                print 'errorlogin: ',e
                InvalidDetails = "The username and/or password you entered is incorrect"
        else:
            InvalidDetails = "Please enter correct details"
    print 'req form'
    # import pusher
    #
    # pusher_client = pusher.Pusher(
    #     app_id='267805',
    #     key='896f67f3b91c49de3343',
    #     secret='6b7bd633bfad598c145b',
    #     # ssl=True
    # )
    #
    # pusher_client.trigger('test_channel', 'my_event', {'message': 'hello world'})
    # return render(request, 'moments/homev3.html',{
    return render(request, 'vendroid/demov2/bride_groom_splah/bride_groom_splah_login.html',{
                 'form':form,
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                 'req_form':req_form,
                 'pre_register':pre_register,
                 'request_success_form':request_success_form,
                })


from django.core.urlresolvers import reverse
@csrf_exempt
def login_professional(request):
    form=loginForm()
    request_success_form = False
    InvalidDetails = None
    if request.method== 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user_auth = authenticate(username=username, password=password)
            try:
                print user_auth
                if user_auth.is_active:
                    user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth_login(request, user_auth)
                    print 'auth'
                    return HttpResponseRedirect(reverse('vendors__profile'))
                else:
                    InvalidDetails = "This account has been deavtivated."
            except Exception as e:
                print e
                InvalidDetails = "The username and/or password you entered is incorrect"
        else:
            InvalidDetails = "Please Enter Details Correctly"
    print 'req form'
    # return render(request, 'moments/home_professional.html',{
    return render(request, 'moments/yapjoy_splash_landing.html',{
                 'form':form,
                 'InvalidDetails':InvalidDetails,
                 'request_success_form':request_success_form,
                })




@csrf_exempt
def admin_login(request):
    form=loginForm()
    registerform=NewRegForm()
    InvalidDetails = None
    if request.method== 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user_auth = authenticate(username=username, password=password)
            try:
                sub = None
                if user_auth.is_active:
                    if user_auth.is_staff:
                        user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                        auth_login(request, user_auth)
                        return HttpResponseRedirect('/crm/mediakit/')
                    InvalidDetails = "Only staff can login."
                else:
                    InvalidDetails = "This account has been deavtivated."
            except Exception as e:
                print e
                InvalidDetails = "The username and/or password you entered is incorrect"
        else:
            InvalidDetails = "Enter correct details."

    return render(request, 'vendroid/login.html',{
                 'form':form,
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                })

def registeration_wizard(request, code):
    sub = get_object_or_404(SubscriptionCode, code=code, is_registered=False)
    form = registrationWizard()
    user = sub.user
    if request.POST:
        form =  registrationWizard(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            type = data['type']
            password = data['password']
            profile = user.userprofile
            profile.type = type
            profile.save()
            user.set_password(password)
            user.save()
            sub.is_registered = True
            sub.save()
            if type == UserProfile.PROFESSIONAL:
                try:
                    company = Company.objects.get_or_create(userprofile=profile)
                except Exception as e:
                    print e
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return HttpResponseRedirect('/')
    return render(request, 'vendroid/registration/wizard/choose_profile.html',{
        'form':form,
        'user':user,
    })

def register(request):
    registerform=NewRegForm()
    InvalidDetails = None
    if request.method== 'POST':
        if 'confirm_password' in request.POST:
            registerform=NewRegForm(request.POST)
            if registerform.is_valid():
                data = registerform.cleaned_data
                first_name = data['first_name']
                last_name = data['last_name']
                email = data['email']
                password = data['password']
                type = data['type']
                user = User.objects.create(email=email, username=email, first_name=first_name, last_name=last_name)
                user.set_password(password)
                user.save()
                profile = user.userprofile
                profile.type = type
                profile.save()

                # if profile.type == UserProfile.GROOM or profile.type == UserProfile.BRIDE or profile.type == UserProfile.UNKNOWNPROFILE:
                #     Product.objects.create(title='Bridal Attire',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Beauty',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Bridal Registry',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Caterers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Flowers',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Equipment Rental',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Rehearsal Dinner',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Favors',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Honeymoon',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Invitations',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Transportation',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Photography',user=user,status=Product.PENDING)
                #     Product.objects.create(title='Videography',user=user,status=Product.PENDING)
                if type == UserProfile.PROFESSIONAL:
                    company = Company.objects.create(userprofile=profile)
                message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)
                print 'auth'
                return HttpResponseRedirect('/dashboard/')
            else:
                InvalidDetails = "Please Enter Details Correctly"

    return render(request, 'vendroid/register.html',{
                 'registerform':registerform,
                 'InvalidDetails':InvalidDetails,
                })

def subscribtionCode(request, code):
    subscribed_user = SubscriptionCode.objects.get(code=code)
    user = subscribed_user.user
    if subscribed_user.is_subscribed:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect('/')
    subform=subscriptionForm()
    InvalidDetails = None
    profile = user.userprofile
    message = "To continue using YapJoy, users are required to pay a small membership Fee of $30/year <h4><strike>(reduced from $99/year for a limited time)</strike></h4>. Kindly provide the information below to continue."
    if profile.type == UserProfile.PROFESSIONAL:
        message = "The registration charges are $30 / 3 months. Kindly provide the information below to register an account."
    print "here in this method"
    if request.method== 'POST':
        subform=subscriptionForm(request.POST)
        if subform.is_valid():
            data = subform.cleaned_data
            print "is_valid"
            try:
                print 'valid'
               # user = User.objects.get(id=1)
                amount_coins = 30
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
                    profile.stripe_id = stripe_customer.id
                profile.save()
                print 'about to response'
                response = stripe.Charge.create(
                amount=int(100) * int(str(amount_coins)),  # Convert dollars into cents
                currency="usd",
                customer=profile.stripe_id,
                description=user.email,
                )


                print response
                if response:  # handle invalid response
                    print 'PAYMENT DONE'
                    # profile.amount+=credit.credits
                    from yapjoy_accounts.models import Transaction, TransactionHistory
                    Transaction.objects.create(user=user, amount =str(amount_coins), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                    TransactionHistory.objects.create(user=user, event="Credit deposited to the account.", amount=int(str(amount_coins)))
                    profile.save()
                    successMessage = "Credit has been added successfully."
                    # send_donation_email(tplVar, user.email)
                    # return HttpResponseRedirect('/account/')

                    # try:
                    #     message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                    #     send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                    # except Exception as e:
                    #     print e
                    #     print "email not sent"
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    subscribed_user.is_subscribed = True
                    subscribed_user.save()
                    SubscribedUsers.objects.create(user=user,
                                                   subscription_date=datetime.now().date(),
                                                   no_of_months=3,
                                                   amount=30)
                    auth_login(request, user)
                    return HttpResponseRedirect('/')
            except Exception as e:
                print 'here error:', e
                InvalidDetails = "Your card was declined."
        else:
            InvalidDetails = "Please Enter Details Correctly"

    return render(request, 'vendroid/registration/subscription.html',{
                 'subform':subform,
                 'InvalidDetails':InvalidDetails,
                 'message':message,
                })

def subscribe(request):
    subscribed_user = SubscriptionCode.objects.get(user=request.user)
    user = subscribed_user.user
    amount_coins = 12

    if subscribed_user.is_subscribed:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect('/')
    subform=subscriptionForm()
    InvalidDetails = None
    profile = user.userprofile
    message = "Congratulations ! Your subscription has been reduced to $12/year ( reduced from $30/year). Please provide your credit card information. Please note that you can cancel anytime."
    if profile.type == UserProfile.PROFESSIONAL:
        message = "The registration charges are $30 / 3 months. Kindly provide the information below to register an account."
        amount_coins = 30
    print "here in this method"
    if request.method== 'POST':
        subform=subscriptionForm(request.POST)
        if subform.is_valid():
            data = subform.cleaned_data
            print "is_valid"
            try:
                print 'valid'
               # user = User.objects.get(id=1)

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
                    profile.stripe_id = stripe_customer.id
                profile.save()
                print 'about to response'
                response = stripe.Charge.create(
                amount=int(100) * int(str(amount_coins)),  # Convert dollars into cents
                currency="usd",
                customer=profile.stripe_id,
                description=user.email,
                )


                print response
                if response:  # handle invalid response
                    print 'PAYMENT DONE'
                    # profile.amount+=credit.credits
                    from yapjoy_accounts.models import Transaction, TransactionHistory
                    Transaction.objects.create(user=user, amount =str(amount_coins), status=Transaction.COMPLETED,response=response, transaction_id=response['balance_transaction']  )
                    TransactionHistory.objects.create(user=user, event="Credit deposited to the account.", amount=int(str(amount_coins)))
                    profile.save()
                    successMessage = "Credit has been added successfully."
                    # send_donation_email(tplVar, user.email)
                    # return HttpResponseRedirect('/account/')

                    # try:
                    #     message = 'Dear %s<br /><br />Kindly click the followng link to activate your account.<br /><br /><a href="%s%s%s" target="_blank" class="btn btn-primary btn-block">Activate Now</a> '%(user.get_full_name(),SITE_NAME,'activate/',profile.activation_id)
                    #     send_email(sendTo=email, title="New Registration Email Verification", message=message, subject="YapJoy Email Verification")
                    # except Exception as e:
                    #     print e
                    #     print "email not sent"
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    subscribed_user.is_subscribed = True
                    subscribed_user.save()
                    SubscribedUsers.objects.create(user=user,
                                                   subscription_date=datetime.now().date(),
                                                   no_of_months=3,
                                                   amount=30)
                    auth_login(request, user)
                    print 'auth'
                    return render(request, 'vendroid/registration/subscription.html',{
                         'subform':subform,
                         'InvalidDetails':InvalidDetails,
                         'message':message,
                         'redirect':'redirect',
                        })

            except Exception as e:
                print 'here error:', e
                InvalidDetails = e
        else:
            InvalidDetails = "Please Enter Details Correctly"

    return render(request, 'vendroid/registration/subscription.html',{
                 'subform':subform,
                 'InvalidDetails':InvalidDetails,
                 'message':message,
                })

import operator
def get_recommend_users(self, user):
    profile = user.userprofile
    users = None
    # interest = []
    # obj_list = []
    # if profile.looking_for:
    #     interest = profile.looking_for
    #     if profile.type == UserProfile.PROFESSIONAL:
    #         obj_list = [obj for obj in UserProfile.objects.filter(~Q(looking_for=UserProfile.PROFESSIONAL)) if any(name in obj.looking_for for name in interest)]
    #     else:
    #         obj_list = [obj for obj in UserProfile.objects.filter(type=UserProfile.PROFESSIONAL) if any(name in obj.looking_for for name in interest)]
    #     print obj_list
    # print interest
    # # ob_list = reduce(lambda x, y: x | y, [Q(looking_for__icontains=word) for word in interest])
    # interest = profile.looking_for
    # if interest:
    #     interest = interest.split(',')
    # query = reduce(operator.or_, (Q(looking_for__icontains = item) for item in interest))
    #print ob_list
    # if not profile.type == UserProfile.PROFESSIONAL:
    #     users = UserProfile.objects.filter(type=UserProfile.PROFESSIONAL).exclude(id=user.userprofile.id).order_by('-subscribed')#.values('userprofile')#UserProfile.objects.filter(type=UserProfile.PROFESSIONAL).filter(query).select_related('user')
    # else:
    #     users = UserProfile.objects.filter(~Q(type=UserProfile.PROFESSIONAL)).exclude(id=user.userprofile.id).order_by('-created_at')
    return UserProfile.objects.all().exclude(id=profile.id).order_by('-subscribed','-created_at')

from yapjoy_files.models import Register_Event, Invoice_Event, BulkInvoices, EventInvoiceRequest, InvoiceRegisterVendor
@login_required(login_url="/login/")
def invoices(request):
    user = request.user
    invoices = EventInvoiceRequest.objects.filter(Q(event_invoice__email__iexact=user.username)|Q(event_invoice__email__iexact=user.email)).order_by('created_at')
    # events = Register_Event.objects.filter(email=user.email).values_list('id', flat=True)
    # invoices = None
    # invoice_id = None
    # if "invoice_id" in request.GET:
    #     invoice_id = request.GET['invoice_id']
    #     print 'invoice id: ',invoice_id
    # if "invoice_id" in request.POST:
    #     invoice_id = request.POST.get('invoice_id')
    #     invoice = Invoice_Event.objects.get(id=invoice_id, registered_event__email=user.email)
    #     invoice.is_signed = True
    #     invoice.save()
    #     return HttpResponseRedirect('/invoices/pay/%s/'%(invoice.id))
    # try:
    #     invoices = EventInvoiceRequest.objects.filter(event_invoice__email__exact=user.email)
    # except Exception as e:
    #     print e
    #     raise Http404
    #
    # invoices_bulk = BulkInvoices.objects.filter(email=user.email)#.values_list('id', flat=True)
    # # invoices = None
    # # invoice_id = None
    # invoice_id_bulk = None
    # if "invoice_id_bulk" in request.GET:
    #     invoice_id_bulk = request.GET['invoice_id_bulk']
    # if "invoice_id_bulk" in request.POST:
    #     invoice_id_bulk = request.POST.get('invoice_id_bulk')
    #     invoice = BulkInvoices.objects.get(id=invoice_id_bulk, email=user.email)
    #     for o in invoice.invoice_event.all():
    #         o.is_signed = True
    #         o.save()
    #     invoice.is_signed = True
    #     invoice.save()
    #     return HttpResponseRedirect('/invoices/bulk/pay/%s/'%(invoice.id))
    #
    # print invoices
    print invoices, invoices.count()
    return render(request, 'vendroid/invoices/invoices.html', {
        'invoices':invoices,
        # 'invoices_bulk':invoices_bulk,
        # 'invoice_id':invoice_id,
        # 'invoice_id_bulk':invoice_id_bulk,
    })
@login_required(login_url="/login/")
def invoices_bulk(request):
    user = request.user
    invoices = BulkInvoices.objects.filter(email=user.email)#.values_list('id', flat=True)
    # invoices = None
    invoice_id = None
    if "invoice_id" in request.GET:
        invoice_id = request.GET['invoice_id']
    if "invoice_id" in request.POST:
        invoice_id = request.POST.get('invoice_id')
        invoice = BulkInvoices.objects.get(id=invoice_id, email=user.email)
        invoice.is_signed = True
        invoice.save()
        return HttpResponseRedirect('/invoices/bulk/pay/%s/'%(invoice.id))
    # try:
    #     invoices = Invoice_Event.objects.filter(registered_event_id__in=events)
    # except Exception as e:
    #     print e
    #     raise Http404

    print invoices
    return render(request, 'vendroid/invoices/invoices_bulk.html', {
        'invoices':invoices,
        'invoice_id':invoice_id,
    })




from yapjoy_files.forms import CreditCardForm
# @login_required(login_url="/login/")
def invoices_pay(request, code):
    print "inside invoices main page"
    invoice = None
    event = None
    user = None
    total_amount = 0

    try:
        print code
        invoice = EventInvoiceRequest.objects.get(code=code)
        try:
            user = User.objects.get(email__iexact=invoice.event_invoice.email,
                                    username__iexact=invoice.event_invoice.email)
        except:
            user = User.objects.create(email__iexact=invoice.event_invoice.email,
                                       username__iexact=invoice.event_invoice.email)
            user.first_name = invoice.event_invoice.register_event.name
            user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        print invoice.status
        if invoice.status == EventInvoiceRequest.PENDING:
            invoice.status = EventInvoiceRequest.VIEWED
            invoice.save()

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
        # invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, registered_event__email=user.email)
        # event = invoice.registered_event.event
        # if not invoice.is_signed:
        #     return HttpResponseRedirect('/invoices/')
    except Exception as e:
        print e
        raise Http404
    profile = user.userprofile
    company = profile.userprofile_company
    form = CreditCardForm()
    # print invoice
    if request.method == "POST":
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = "sk_live_n8WrsUoKt0Esb2cfUAIBHWgn"
            token = request.POST.get('stripe_token')
            customer = stripe.Customer.create(email=invoice.event_invoice.email,

                                              source=token)
            charge = stripe.Charge.create(
                                            amount=(total_amount*100), # in cents
                                            currency="usd",
                                            customer=customer.id)
            # invoice.payment_date = datetime.now().date()
            invoice.transaction_id = charge.stripe_id
            invoice.status = EventInvoiceRequest.PAID
            invoice.save()
            e_invoice = invoice.event_invoice
            if type == EventInvoiceRequest.BALANCE1:
                e_invoice.transaction_id_balance1 = charge.stripe_id
            if type == EventInvoiceRequest.BALANCE2:
                e_invoice.transaction_id_balance2 = charge.stripe_id
            if type == EventInvoiceRequest.BALANCE3:
                e_invoice.transaction_id_balance3 = charge.stripe_id
            e_invoice.save()

    today = datetime.now().date()
    return render(request, 'vendroid/invoices/invoices_pay.html', {
        'invoice':invoice,
        'today':today,
        'profile':profile,
        'company':company,
        'form':form,
        'event':event,
        'invoices':invoices,
        'type':type,
        'total_amount':total_amount,
    })



from yapjoy_files.models import Notes, Register_Event_Aggrement
# @login_required(login_url="/login/")
def invoices_deposit_pay_main(request, code, code2):
    print "inside invoices main page"
    invoice = None
    event = None
    error_message = None
    user = None
    is_list = False
    total_amount = 0
    try:
        print code
        invoice = EventInvoiceRequest.objects.get(code=code)
        if invoice.status == EventInvoiceRequest.CANCEL:
            raise Http404
        try:
            user = User.objects.get(email__iexact=invoice.event_invoice.email, username__iexact=invoice.event_invoice.email)
        except:
            user = User.objects.create(email__iexact=invoice.event_invoice.email, username__iexact=invoice.event_invoice.email)
            user.first_name = invoice.event_invoice.register_event.name
            user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        print invoice.status
        if invoice.status == EventInvoiceRequest.PENDING:
            invoice.status = EventInvoiceRequest.VIEWED
            invoice.save()

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
    except Exception as e:
        print e
        raise Http404
    # user = request.user
    profile = user.userprofile
    form_check = checkForm()
    # company = profile.userprofile_company
    form = CreditCardForm()
    # print invoice
    text_to_append = ""
    try:
        event_obj = invoice.event_invoice.register_event
        if event_obj:
            if event_obj.is_partner_vendor:
                text_to_append = "<br /><br />You have been offered Partner Vendor status. One of the benefits of being a partner vendor is that your business is listed on BayAreaWeddingFairs.com website<br />Please send us following so we can list you on our website.<br /><br /><li>A 400x400 pixel picture with your business logo</li><li>Your business website link (URL)</li><li>Contact Information</li><li>A 60 word description of your business.</li><br /><br />Please send this information to Steve@BayAreaWeddingFairs.com<br /><br />Thank you"
    except Exception as e:
        print "partner vendor failed: ",e
    agreement = get_object_or_404(Register_Event_Aggrement, code=code2)
    if "invoice-form-check" in request.POST:
        print 'inside invoice-form-check'
        form_check = checkForm(request.POST)
        if form_check.is_valid():
            print 'agreement is accepted'
            agreement.status = Register_Event_Aggrement.ACCEPTED
            agreement.save()
            # invoice.transaction_id = "Check"
            invoice.status = EventInvoiceRequest.SIGNED
            invoice.save()
            e_invoice = invoice.event_invoice
            e_invoice.transaction_id_deposit_date = datetime.now()
            e_invoice.save()

            # e_invoice.transaction_id_deposit = "Check"
            # e_invoice.save()
            context = {
                'message': "%s (%s) with email %s has accepted the invoice with id: %s." % (
                invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,
                agreement.email, agreement.id),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                         'info@bayareaweddingfairs.com',
                                         ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            context = {
                'message': "%s (%s)<br /><br />Thank you for working with Bay Area Wedding Fairs. You have accepted the Agreement with all terms and conditions. <br /><br />To view all the invoices, goto the following link:<br /><br /> <a href='https://www.yapjoy.com/invoices/'>Invoices</a>%s<br /><br />Please let us know if you have any questions<br /><br /><a target='_blank' class='btn btn-primary' href='https://www.yapjoy.com/feedback/'>Contact Us</a>" % (
                invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,text_to_append),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                         from_email='info@bayareaweddingfairs.com', to=[agreement.email],
                                         cc=['info@bayareaweddingfairs.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            reg_rec = e_invoice.register_event
            # reg_rec.record_amount_due()
            reg_rec.amount_due = reg_rec.get_amount_due()
            reg_rec.total_amount = reg_rec.get_amount_total()
            reg_rec.save()

    elif "invoice-form-cash" in request.POST:
        print 'inside invoice-form-check'
        form_check = checkForm(request.POST)
        if form_check.is_valid():
            print 'agreement is accepted cash'
            agreement.status = Register_Event_Aggrement.ACCEPTED
            agreement.save()
            # invoice.transaction_id = "Cash"
            invoice.status = EventInvoiceRequest.SIGNED
            invoice.save()
            e_invoice = invoice.event_invoice
            e_invoice.transaction_id_deposit_date = datetime.now()
            e_invoice.save()
            # e_invoice.transaction_id_deposit = "Cash"
            # e_invoice.save()
            context = {
                'message': "%s (%s) with email %s has accepted the invoice with id: %s." % (
                invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,
                agreement.email, agreement.id),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                         'info@bayareaweddingfairs.com',
                                         ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            context = {
                 'message': "%s (%s)<br /><br />Thank you for working with Bay Area Wedding Fairs. You have accepted the Agreement with all terms and conditions. <br /><br />To view all the invoices, goto the following link:<br /><br /> <a href='https://www.yapjoy.com/invoices/'>Invoices</a>%s<br /><br />Please let us know if you have any questions<br /><br /><a target='_blank' class='btn btn-primary' href='https://www.yapjoy.com/feedback/'>Contact Us</a>" % (invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,text_to_append),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                         from_email='info@bayareaweddingfairs.com', to=[agreement.email],
                                         cc=['info@bayareaweddingfairs.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            reg_rec = e_invoice.register_event
            # reg_rec.record_amount_due()
            reg_rec.amount_due = reg_rec.get_amount_due()
            reg_rec.total_amount = reg_rec.get_amount_total()
            reg_rec.save()
    elif "add-check-number" in request.POST:
        check_no = request.POST.get('check_no')
        invoice.check_no = check_no
        invoice.save()
    elif request.method == "POST":
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            token = request.POST.get('stripe_token')
            customer = None
            try:
                customer = stripe.Customer.create(email=invoice.event_invoice.email,

                                                  source=token)
            except Exception as e:
                error_message = e
            if customer:
                profile.stripe_id_bawf = customer.id
                profile.save()
                charge = None
                try:
                    charge = stripe.Charge.create(
                        amount=(total_amount * 100),  # in cents
                        currency="usd",
                        customer=customer.id)
                except Exception as e:
                    charge = None
                    error_message = e
                if charge:
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
                    agreement.status = Register_Event_Aggrement.ACCEPTED
                    agreement.save()

                    context = {
                        'message': "%s (%s) with email %s has accepted the invoice with id: %s." % (invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,agreement.email, agreement.id),
                        'title': "Accepted: Bay Area Wedding Fairs Agreement",
                    }
                    html_content = render_to_string('email/bawf_native_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                                 'info@bayareaweddingfairs.com',
                                                 ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    context = {
                        'message': "%s (%s)<br /><br />Thank you for working with Bay Area Wedding Fairs. You have accepted the Agreement with all terms and conditions. <br /><br />To view all the invoices, goto the following link:<br /><br /> <a href='https://www.yapjoy.com/invoices/'>Invoices</a>%s<br /><br />Please let us know if you have any questions<br /><br /><a target='_blank' class='btn btn-primary' href='https://www.yapjoy.com/feedback/'>Contact Us</a>" % (
                        invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,text_to_append),
                        'title': "Accepted: Bay Area Wedding Fairs Agreement",
                    }
                    html_content = render_to_string('email/bawf_native_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                                 from_email='info@bayareaweddingfairs.com', to=[agreement.email],
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
    today = datetime.now().date()

    if not agreement.status == Register_Event_Aggrement.VIEWED and not agreement.status == Register_Event_Aggrement.ACCEPTED and not agreement.status == Register_Event_Aggrement.REJECTED:
        agreement.status = Register_Event_Aggrement.VIEWED
        agreement.save()
        context = {
            'message': "%s (%s) with email %s has viewed the invoice with id: %s." % (invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,agreement.email, invoice.id),
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
        pass
    if "decline" in request.POST:
        agreement.status = Register_Event_Aggrement.REJECTED
        agreement.save()
        context = {
            'message': "%s (%s) with email %s has rejected the invoice with id: %s." % (invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name, agreement.email, agreement.id),
            'title': "Rejected: Bay Area Wedding Fairs Agreement",
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
    invoices_agree = agreement.invoices.all()
    inv = None
    reg = None
    notes = None
    is_check = False
    is_cash = False
    pv_price_list = None
    if invoices_agree:
        for in_ag in invoices_agree:
            if in_ag.pv_prize_offered:
                pv_price_list = in_ag
    if invoices_agree:
        inv = invoices_agree[0]
        reg = invoices_agree[0].register
        if inv.payment_method == InvoiceRegisterVendor.CHECK:
            is_check = True
        elif inv.payment_method == InvoiceRegisterVendor.CASH:
            is_cash = True
        reg_tosend = invoices_agree.values_list('register', flat=True)
        notes = Notes.objects.filter(exhibitor__in=reg_tosend)
    event_invoice_info = invoice.event_invoice
    # event_invoice__object = event_invoice_info.event_invoice
    event_list = ['Signed', 'Paid']
    return render(request, 'vendroid/CRM/deposit_agreement.html', {
        'key':settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'event_list':event_list,
        'invoice':invoice,
        'event_invoice__object':event_invoice_info,
        'today':today,
        'profile':profile,
        # 'company':company,
        'form':form,
        'event':event,
        'invoices':invoices,
        'type':type,
        'total_amount':total_amount,
        'is_check': is_check,
        'is_cash': is_cash,
        #------------------------------
        'agreement': agreement,
        'invoices_agree': invoices_agree,
        'notes': notes,
        'inv': inv,
        'reg': reg,
        'event_invoice_info': event_invoice_info,
        'form_check': form_check,
        'is_list': is_list,
        'error_message': error_message,
        'pv_price_list': pv_price_list,
    })






from yapjoy_files.models import Notes, Register_Event_Aggrement, CardChange
from yapjoy_files.forms import CreditCardCreationForm
# @login_required(login_url="/login/")
@csrf_exempt
def card_change_view(request, code):
    print code
    is_customer = None
    change_card = None
    user = None
    profile = None
    card_errors = None
    success_card_change = None
    try:
        change_card = CardChange.objects.get(code=code)
        user = User.objects.get(email__iexact=change_card.email)
        profile = user.userprofile
        if change_card.is_expired:
            success_card_change = "To update your card again, please contact with info@bayareaweddingfairs.com"
    except:
        raise Http404
    form = CreditCardCreationForm()
    if request.method == "POST":
        form = CreditCardCreationForm(request.POST)
        if form.is_valid():
            stripe_token = request.POST.get('stripe_token')
            print stripe_token
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            try:
                print 'stripe token is found'
                stripe_customer = stripe.Customer.create(
                    email=user.email,
                    card=request.POST.get("stripe_token")
                )
                print 'customer: ', stripe_customer

                if stripe_customer:
                    profile.stripe_id_bawf = stripe_customer.id
                    profile.save()
                success_card_change = "Your card is successfully updated."
                change_card.is_expired = True
                change_card.save()
                context = {
                    'message': "Your card has been updated successfully.<br /><br />For more queries, please contact info@bayareaweddingfairs.com.</b>",
                    'title': "Bay Area Wedding Fairs Card Change Sucessful.",
                }
                html_content = render_to_string('email/bawf_native_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Card Change Sucessful", text_content,
                                             'info@bayareaweddingfairs.com',
                                             [user.email, 'wasim@yapjoy.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                context = {
                    'message': "Vendor %s (%s) has updated the card successfully."%(user.get_full_name(), user.email),
                    'title': "Bay Area Wedding Fairs Card Change Sucessful.",
                }
                html_content = render_to_string('email/bawf_native_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Card Change Sucessful", text_content,
                                             'info@bayareaweddingfairs.com',
                                             ['adeel@yapjoy.com', 'wasim@yapjoy.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print e
                card_errors = str(e)
    try:
        user = User.objects.get(email__iexact=change_card.email)
        profile = user.userprofile
        if profile.stripe_id_bawf:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            is_customer_data = stripe.Customer.retrieve(
                profile.stripe_id_bawf)  # .cards.all(limit=1)['data'][0]['last4']
            print 'is customer: ', is_customer_data.sources['data'][0]['last4']
            is_customer = is_customer_data.sources['data'][0]['last4']
    except Exception as e:
        print 'inside customer exception: ', e
        customer_failed = True


    return render(request, 'vendroid/CRM/card_change.html', {
        'form':form,
        'is_customer':is_customer,
        'key':settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'success_card_change':success_card_change,
        'card_errors':card_errors,
        'user':user,
        'profile':profile,

    })





from django.contrib.admin.views.decorators import staff_member_required
from yapjoy_files.forms import checkForm
@login_required(login_url='/crm/login/')
@staff_member_required
def invoices_deposit_view_main(request, code, code2):
    print "inside invoices main page"
    invoice = None
    event = None
    user = None
    profile = None
    error_message = None
    is_list = False
    total_amount = 0
    try:
        print code
        invoice = EventInvoiceRequest.objects.get(code=code)
        try:
            user = User.objects.get(email__iexact=invoice.event_invoice.email, username__iexact=invoice.event_invoice.email)
        except:
            user = User.objects.create(email__iexact=invoice.event_invoice.email, username__iexact=invoice.event_invoice.email)
            user.first_name = invoice.event_invoice.register_event.name
            user.save()
        try:
            profile = user.userprofile
        except:
            pass
        print invoice.status
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
    except Exception as e:
        print e
        raise Http404
    # user = request.user
    profile = user.userprofile
    form_check = checkForm()
    # company = profile.userprofile_company
    form = CreditCardForm()
    agreement = get_object_or_404(Register_Event_Aggrement, code=code2)
    if "invoice-form-check" in request.POST:
        print 'inside invoice-form-check'
        form_check = checkForm(request.POST)
        if form_check.is_valid():
            print 'agreement is accepted'
            agreement.status = Register_Event_Aggrement.ACCEPTED
            agreement.save()
            invoice.transaction_id = "Check"
            invoice.status = EventInvoiceRequest.SIGNED
            invoice.save()
            e_invoice = invoice.event_invoice
            # e_invoice.transaction_id_deposit = "Check"
            # e_invoice.save()
            reg_rec = e_invoice.register_event
            # reg_rec.record_amount_due()
            reg_rec.amount_due = reg_rec.get_amount_due()
            reg_rec.total_amount = reg_rec.get_amount_total()
            reg_rec.save()

    elif "add-check-number" in request.POST:
        check_no = request.POST.get('check_no')
        invoice.check_no = check_no
        invoice.status = EventInvoiceRequest.PAID
        invoice.signing_date = str(datetime.now())
        invoice.save()
        e_invoice = invoice.event_invoice
        e_invoice.transaction_id_deposit = "Check"
        e_invoice.save()
        reg_rec = invoice.event_invoice.register_event
        # reg_rec.record_amount_due()
        reg_rec.amount_due = reg_rec.get_amount_due()
        reg_rec.total_amount = reg_rec.get_amount_total()
        reg_rec.save()
    elif "mark-cash-paid" in request.POST:
        check_no = request.POST.get('check_no')
        invoice.check_no = "Cash"
        invoice.status = EventInvoiceRequest.PAID
        e_invoice = invoice.event_invoice
        e_invoice.transaction_id_deposit = "Cash"
        e_invoice.save()
        invoice.signing_date = str(datetime.now())
        invoice.save()
        reg_rec = invoice.event_invoice.register_event
        # reg_rec.record_amount_due()
        reg_rec.amount_due = reg_rec.get_amount_due()
        reg_rec.total_amount = reg_rec.get_amount_total()
        reg_rec.save()
    elif "customer_charge_signal" in request.POST:
        print 'inside post'
        # form = CreditCardForm(request.POST)
        # if form.is_valid():
        #     data = form.cleaned_data
        #     print data
        stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
        # token = request.POST.get('stripe_token')

        # customer = stripe.Customer.create(email=invoice.event_invoice.email,
        #
        #                                   source=token)
        # if customer:
        #     profile.stripe_id_bawf = customer.id
        #     profile.save()
        charge = None
        try:
            charge = stripe.Charge.create(
                amount=(total_amount * 100),  # in cents
                currency="usd",
                customer=profile.stripe_id_bawf)
        except Exception as e:
            error_message = e
        if charge:
            # invoice.payment_date = datetime.now().date()
            invoice.transaction_id = charge.stripe_id
            invoice.status = EventInvoiceRequest.PAID
            invoice.save()
            e_invoice = invoice.event_invoice
            e_invoice.transaction_id_deposit = charge.stripe_id
            e_invoice.save()
            reg_event = e_invoice.register_event
            # reg_event.record_amount_due()
            reg_event.amount_due = reg_event.get_amount_due()
            reg_event.total_amount = reg_event.get_amount_total()
            reg_event.save()
            agreement.status = Register_Event_Aggrement.ACCEPTED
            agreement.save()
            context = {
                'message': "%s (%s) with email %s has accepted the invoice with id: %s." % (
                invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,
                agreement.email, agreement.id),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                         'info@bayareaweddingfairs.com',
                                         ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            context = {
                'message': "%s (%s)<br /><br />Thank you for working with Bay Area Wedding Fairs. You have accepted the Agreement with all terms and conditions. Please let us know if you have any questions<br /><br /><a target='_blank' class='btn btn-primary' href='https://www.yapjoy.com/feedback/'>Contact Us</a><br /><br />To view all the invoices, goto the following link:<br /><br /> <a href='https://www.yapjoy.com/invoices/'>Invoices</a>" % (
                    invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name),
                'title': "Accepted: Bay Area Wedding Fairs Agreement",
            }
            html_content = render_to_string('email/bawf_native_email.html', context=context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                         from_email='info@bayareaweddingfairs.com', to=[agreement.email],
                                         cc=['info@bayareaweddingfairs.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    elif request.method == "POST":
        print 'inside post'
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print data
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            token = request.POST.get('stripe_token')
            customer = None
            try:
                customer = stripe.Customer.create(email=invoice.event_invoice.email,

                                                  source=token)
            except Exception as e:
                error_message = e
            if customer:
                profile.stripe_id_bawf = customer.id
                profile.save()
                charge = None
                try:
                    charge = stripe.Charge.create(
                        amount=(total_amount * 100),  # in cents
                        currency="usd",
                        customer=customer.id)
                except Exception as e:
                    error_message = e
                if charge:
                    # invoice.payment_date = datetime.now().date()
                    invoice.transaction_id = charge.stripe_id
                    invoice.status = EventInvoiceRequest.PAID
                    invoice.save()
                    e_invoice = invoice.event_invoice
                    e_invoice.transaction_id_deposit = charge.stripe_id
                    e_invoice.save()
                    reg_event = e_invoice.register_event
                    # reg_event.record_amount_due()
                    reg_event.amount_due = reg_event.get_amount_due()
                    reg_event.total_amount = reg_event.get_amount_total()
                    reg_event.save()
                    agreement.status = Register_Event_Aggrement.ACCEPTED
                    agreement.save()
                    context = {
                        'message': "%s (%s) with email %s has accepted the invoice with id: %s." % (
                        invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name,
                        agreement.email, agreement.id),
                        'title': "Accepted: Bay Area Wedding Fairs Agreement",
                    }
                    html_content = render_to_string('email/bawf_native_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
                                                 'info@bayareaweddingfairs.com',
                                                 ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    context = {
                        'message': "%s (%s)<br /><br />Thank you for working with Bay Area Wedding Fairs. You have accepted the Agreement with all terms and conditions. Please let us know if you have any questions<br /><br /><a target='_blank' class='btn btn-primary' href='https://www.yapjoy.com/feedback/'>Contact Us</a><br /><br />To view all the invoices, goto the following link:<br /><br /> <a href='https://www.yapjoy.com/invoices/'>Invoices</a>" % (
                            invoice.event_invoice.register_event.name, invoice.event_invoice.register_event.business_name),
                        'title': "Accepted: Bay Area Wedding Fairs Agreement",
                    }
                    html_content = render_to_string('email/bawf_native_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
                                                 from_email='info@bayareaweddingfairs.com', to=[agreement.email],
                                                 cc=['info@bayareaweddingfairs.com'])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

    today = datetime.now().date()

    notes = None
    invoices_agree = agreement.invoices.all()
    inv = None
    reg = None
    notes = None
    is_check = False
    is_cash = False
    print "Invoices agree: ",invoices_agree
    pv_price_list = None
    if invoices_agree:
        for in_ag in invoices_agree:
            if in_ag.pv_prize_offered:
                pv_price_list = in_ag
    if invoices_agree:
        print 'Inside invoice agree'
        inv = invoices_agree[0]
        reg = invoices_agree[0].register
        print inv.payment_method
        if inv.payment_method == InvoiceRegisterVendor.CHECK:
            is_check = True
        elif inv.payment_method == InvoiceRegisterVendor.CASH:
            is_cash = True
        reg_tosend = invoices_agree.values_list('register',flat=True)
        notes = Notes.objects.filter(exhibitor__in=reg_tosend)
    event_invoice_info = invoice.event_invoice
    event_list = ['Signed','Paid','Cancel']
    event_list2 = ['Paid']
    print 'invoice status: ',invoice.status
    last4 = None
    if profile.stripe_id_bawf:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY_BAWF
            customer = stripe.Customer.retrieve(profile.stripe_id_bawf)
            last4 = customer.sources['data'][0]['last4']
        except Exception as e:
            print "Customer getting error: ",e

    return render(request, 'vendroid/CRM/deposit_agreement_view.html', {
        'key':settings.STRIPE_PUBLISHABLE_KEY_BAWF,
        'invoice':invoice,
        'event_list':event_list,
        'event_list2':event_list2,
        'today':today,
        'profile':profile,
        'error_message':error_message,
        # 'company':company,
        'form':form,
        'event':event,
        'invoices':invoices,
        'type':type,
        'last4':last4,
        'total_amount':total_amount,
        'is_check':is_check,
        'is_cash':is_cash,
        #------------------------------
        'agreement': agreement,
        'invoices_agree': invoices_agree,
        'notes': notes,
        'inv': inv,
        'reg': reg,
        'event_invoice_info': event_invoice_info,
        'form_check': form_check,
        'profile': profile,
        'is_list': is_list,
        'pv_price_list': pv_price_list,
    })


#
# from yapjoy_files.forms import CreditCardForm
# from yapjoy_files.models import Notes, Register_Event_Aggrement
# @login_required(login_url="/login/")
# def invoices_deposit_pay_main(request, code, code2):
#     # print "inside invoices"
#     # user = request.user
#     # profile = user.userprofile
#     # invoice = None
#     # event = None
#     # total_amount = 0
#     # company = profile.userprofile_company
#     # form = CreditCardForm()
#     # try:
#     #     print code
#     #     invoice = EventInvoiceRequest.objects.get(code=code)
#     #     print 'invoice status: ',invoice.status
#     #     if invoice.status == EventInvoiceRequest.PENDING:
#     #         invoice.status = EventInvoiceRequest.VIEWED
#     #         invoice.save()
#     #
#     #     type = invoice.type
#     #     print type
#     #     invoices = invoice.event_invoice.invoices.all()
#     #     for o in invoices:
#     #         if type == EventInvoiceRequest.DEPOSIT:
#     #             total_amount += o.deposit
#     #         if type == EventInvoiceRequest.BALANCE1:
#     #             total_amount += o.balance1
#     #         if type == EventInvoiceRequest.BALANCE2:
#     #             total_amount += o.balance2
#     #         if type == EventInvoiceRequest.BALANCE3:
#     #             total_amount += o.balance3
#     #     # invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, registered_event__email=user.email)
#     #     # event = invoice.registered_event.event
#     #     # if not invoice.is_signed:
#     #     #     return HttpResponseRedirect('/invoices/')
#     # except Exception as e:
#     #     print e
#     #     raise Http404
#     # # print invoice
#     # if request.method == "POST":
#     #     form = CreditCardForm(request.POST)
#     #     if form.is_valid():
#     #         data = form.cleaned_data
#     #         print data
#     #         stripe.api_key = "sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0"
#     #         token = request.POST.get('stripe_token')
#     #         customer = stripe.Customer.create(email=invoice.event_invoice.email,
#     #
#     #                                           source=token)
#     #         charge = stripe.Charge.create(
#     #                                         amount=(total_amount*100), # in cents
#     #                                         currency="usd",
#     #                                         customer=customer.id)
#     #         # invoice.payment_date = datetime.now().date()
#     #         invoice.transaction_id = charge.stripe_id
#     #         invoice.status = EventInvoiceRequest.PAID
#     #         invoice.save()
#     #
#     # today = datetime.now().date()
#     #
#     # agreement = get_object_or_404(Register_Event_Aggrement, code=code2)
#     # if not agreement.status == Register_Event_Aggrement.VIEWED and not agreement.status == Register_Event_Aggrement.ACCEPTED and not agreement.status == Register_Event_Aggrement.REJECTED:
#     #     agreement.status = Register_Event_Aggrement.VIEWED
#     #     agreement.save()
#     #     context = {
#     #         'message': "User with email %s have viewed the invoice with id: %s." % (agreement.email, agreement.id),
#     #         'title': "Viewed: Bay Area Wedding Fairs Invoice",
#     #     }
#     #     html_content = render_to_string('email/bawf_native_email.html', context=context)
#     #     text_content = strip_tags(html_content)
#     #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Viewed", text_content,
#     #                                  'info@bayareaweddingfairs.com',
#     #                                  ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
#     #     msg.attach_alternative(html_content, "text/html")
#     #     msg.send()
#     #     message = "Invoice request sent successfully."
#     # if "accept" in request.POST:
#     #     agreement.status = Register_Event_Aggrement.ACCEPTED
#     #     agreement.save()
#     #     context = {
#     #         'message': "User with email %s has accepted the invoice with id: %s." % (agreement.email, agreement.id),
#     #         'title': "Accepted: Bay Area Wedding Fairs Invoice",
#     #     }
#     #     html_content = render_to_string('email/bawf_native_email.html', context=context)
#     #     text_content = strip_tags(html_content)
#     #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Accepted", text_content,
#     #                                  'info@bayareaweddingfairs.com',
#     #                                  ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
#     #     msg.attach_alternative(html_content, "text/html")
#     #     msg.send()
#     #     context = {
#     #         'message': "Thank you for accepting the agreement no %s with BayAreaWeddingFairs, You will be sent an invoice shortly for the event. <br /><br />Kindly get back to us with an email, or the reply to this email if you have not initiated the above action." % (
#     #             agreement.id),
#     #         'title': "Accepted: Bay Area Wedding Fairs Invoice",
#     #     }
#     #     html_content = render_to_string('email/bawf_native_email.html', context=context)
#     #     text_content = strip_tags(html_content)
#     #     msg = EmailMultiAlternatives(subject="BayAreaWeddingFairs Agreement Accepted", body=text_content,
#     #                                  from_email='info@bayareaweddingfairs.com', to=[agreement.email],
#     #                                  cc=['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
#     #     msg.attach_alternative(html_content, "text/html")
#     #     msg.send()
#     # if "decline" in request.POST:
#     #     agreement.status = Register_Event_Aggrement.REJECTED
#     #     agreement.save()
#     #     context = {
#     #         'message': "User with email %s has rejected the invoice with id: %s." % (agreement.email, agreement.id),
#     #         'title': "Rejected: Bay Area Wedding Fairs Invoice",
#     #     }
#     #     html_content = render_to_string('email/bawf_native_email.html', context=context)
#     #     text_content = strip_tags(html_content)
#     #     msg = EmailMultiAlternatives("BayAreaWeddingFairs Agreement Rejected", text_content,
#     #                                  'info@bayareaweddingfairs.com',
#     #                                  ['info@bayareaweddingfairs.com', 'adeelpkpk@gmail.com'])
#     #     msg.attach_alternative(html_content, "text/html")
#     #     msg.send()
#     # notes = None
#     # # invoices = agreement.invoices
#     # # if invoices:
#     # #     pass
#     # # notes = Notes.objects.filter(exhibitor__id=invoices[0].register)
#     # invoices_agree = agreement.invoices.all()
#     # inv = None
#     # reg = None
#     # notes = None
#     # if invoices_agree:
#     #     inv = invoices_agree[0]
#     #     reg = invoices_agree[0].register
#     #     notes = Notes.objects.filter(exhibitor=reg)
#     # print 'agreement: ',agreement.email
#     # print 'invoice: ',invoice
#     print "inside invoices main page deposit"
#     user = request.user
#     profile = user.userprofile
#     invoice = None
#     event = None
#     total_amount = 0
#     company = profile.userprofile_company
#     form = CreditCardForm()
#     # try:
#     print code
#     invoice = EventInvoiceRequest.objects.get(code=code)
#     print invoice.status
#     if invoice.status == EventInvoiceRequest.PENDING:
#         invoice.status = EventInvoiceRequest.VIEWED
#         invoice.save()
#
#     type = invoice.type
#     print type
#     invoices = invoice.event_invoice.invoices.all()
#     for o in invoices:
#         if type == EventInvoiceRequest.DEPOSIT:
#             total_amount += o.deposit
#         if type == EventInvoiceRequest.BALANCE1:
#             total_amount += o.balance1
#         if type == EventInvoiceRequest.BALANCE2:
#             total_amount += o.balance2
#         if type == EventInvoiceRequest.BALANCE3:
#             total_amount += o.balance3
#             # invoice = Invoice_Event.objects.select_related('registered_event__event', 'registered_event').get(id=id, registered_event__email=user.email)
#             # event = invoice.registered_event.event
#             # if not invoice.is_signed:
#             #     return HttpResponseRedirect('/invoices/')
#     # except Exception as e:
#     #     print e
#     #     raise Http404
#     # print invoice
#     if request.method == "POST":
#         form = CreditCardForm(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             print data
#             stripe.api_key = "sk_test_D8XQLQXVdpI2X03rn0Ycp5Y0"
#             token = request.POST.get('stripe_token')
#             customer = stripe.Customer.create(email=invoice.event_invoice.email,
#
#                                               source=token)
#             charge = stripe.Charge.create(
#                 amount=(total_amount * 100),  # in cents
#                 currency="usd",
#                 customer=customer.id)
#             # invoice.payment_date = datetime.now().date()
#             invoice.transaction_id = charge.stripe_id
#             invoice.status = EventInvoiceRequest.PAID
#             invoice.save()
#     return render(request, 'vendroid/CRM/deposit_agreement.html', {
#         'invoice':invoice,
#         # 'today':today,
#         'profile':profile,
#         'company':company,
#         'form':form,
#         'event':event,
#         'invoices':invoices,
#         # 'invoices_agree':invoices_agree,
#         'type':type,
#         'total_amount':total_amount,
#         # 'event': event,
#         # 'agreement': agreement,
#         # 'invoices': invoices,
#         # 'notes': notes,
#         # 'inv': inv,
#         # 'reg': reg,
#         # 'notes': notes,
#     })
#




from yapjoy_files.forms import CreditCardForm
@login_required(login_url="/login/")
def invoices_pay_bulk(request, id):
    user = request.user
    profile = user.userprofile
    invoice = None
    event = None
    company = profile.userprofile_company
    form = CreditCardForm()
    try:
        invoice = BulkInvoices.objects.get(id=id, email=user.email)
        event = invoice.invoice_event.all()[0].registered_event.event
        if not invoice.is_signed:
            return HttpResponseRedirect('/invoices/bulk/')
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
            for o in invoice.invoice_event.all():
                o.payment_date = datetime.now().date()
                o.transaction_id = charge.stripe_id
                o.status = Invoice_Event.PAID
                o.save()
            invoice.payment_date = datetime.now().date()
            invoice.status = Invoice_Event.PAID
            invoice.save()

    today = datetime.now().date()
    return render(request, 'vendroid/invoices/invoices_pay_bulk.html', {
        'invoice':invoice,
        'today':today,
        'profile':profile,
        'company':company,
        'form':form,
        'event':event,
    })

@login_required(login_url='/login/')
def api_friends(request):

    user_id = None
    name = None
    if request.is_ajax():
        try:
            user_id = request.GET.get('user_id')
        except:
            raise Http404

        print "user_id", user_id

        f = User.objects.get(id=user_id)
        print f
        tf = User.objects.get(id=request.user.id)
        print tf
        friends = Friends.objects.get_or_create(user=tf)
        result = None
        try:
            AllFriends.objects.get(user=f, friends=friends)
            result = "Already a friend"
        except:
            AllFriends.objects.create(user=f, friends=friends)
            result = "Request Sent"

        return HttpResponse(result)

def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def terms_and_conditions(request):
    return render(request, 'pages/terms_and_conditions.html')

def send_email_2(request):
    import csv
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
    count = 0
    with open('emails.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #if ".ca" in row['email']:
            if not row['email'].endswith('.ca') and count <= 200:
                try:
                    count += 1
                    html_content = render_to_string('email/promotion.html')
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives('YapJoy Invitation', text_content, 'YapJoy INC <info@yapjoy.com>', [row['email']])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    print "%d: Email Sent (%s)"%(count, row['email'])
                except:
                    print "%d: Email Failed (%s)"%(count, row['email'])
    return HttpResponse('Job Completed')
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class emails(object):

    def send_emails(self):
        import csv
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
        count = 0
        with open('emails.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #if ".ca" in row['email']:
                if not row['email'].endswith('.ca') and count <= 200:
                    try:
                        count += 1
                        html_content = render_to_string('email/promotion.html')
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives('YapJoy Invitation', text_content, 'YapJoy INC <info@yapjoy.com>', [row['email']])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                        print "%d: Email Sent (%s)"%(count, row['email'])
                    except:
                        print "%d: Email Failed (%s)"%(count, row['email'])
        # return HttpResponse('Job Completed')

    def send_user_emails(self):
        import csv
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
        counter = 0
       # print "here"
        with open('brides_added.csv', 'rU') as csvfile:
           # print csvfile
            reader = csv.DictReader(csvfile)
            #print reader
            for row in reader:
                if counter > -1:
                    #print row
                   # print row['Email']
                    reg_user = ""
                    counter += 1
                    #password = id_generator()
                    try:
                        # user = User.objects.create(username=row['Email'], email=row['Email'], first_name=row['First Name'])
                        # user.set_password(password)
                        # user.save()
                        # userprofile = user.userprofile
                        # userprofile.type = UserProfile.UNKNOWNPROFILE
                        # userprofile.street = row['Address']
                        # userprofile.city = row['City']
                        # userprofile.state = row['State']
                        # userprofile.zip = row['Zipcode']
                        # userprofile.save()
                        # reg_user = RegisteredBrideUsers.objects.create(email=row['Email'])
                        if not "Failed" in row['code']:
                            # print row['email'],row['password'],row['code'],
                            html_content = render_to_string('email/promotion2.html',{
                            'email':row['email'],
                            'password':row['password'],
                            'code':row['code'],
                            })
                            text_content = strip_tags(html_content)
                            msg = EmailMultiAlternatives('New Wedding Planning Social Network', text_content, 'YapJoy INC <info@yapjoy.com>', [row['email']])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                            print "%d,%s,%s,%s,%s"%(counter, row['name'],row['email'],row['password'], row['code'])
                    except Exception as e:
                        #print e
                        print "%d,%s,%s,%s,%s Failed"%(counter,row['name'],row['email'],row['password'], row['code'])
                # if not row['email'].endswith('.ca') and count <= 200:
                #     try:
                #         count += 1
                #     html_content = render_to_string('email/promotion2.html',{
                #         'email':row['Email'],
                #         'password':password,
                #     })
                    # text_content = strip_tags(html_content)
                    # msg = EmailMultiAlternatives('New Wedding Planning Social Network', text_content, 'YapJoy INC <info@yapjoy.com>', [row['Email']])
                    # msg.attach_alternative(html_content, "text/html")
                    # msg.send()
                    #print "%s,%s,%s"%(row['First Name'],row['Email'],password)
                #         print "%d: Email Sent (%s)"%(count, row['email'])
                #     except:
                #         print "%d: Email Failed (%s)"%(count, row['email'])

    # html_content = render_to_string('email/promotion.html')
    # text_content = strip_tags(html_content)
    # msg = EmailMultiAlternatives("YapJoy Invitation", text_content, 'YapJoy INC <info@yapjoy.com>', ['adeelpkpk@gmail.com'])
    # msg.attach_alternative(html_content, "text/html")
    # msg.send()
    # print 'Sent'
    # return HttpResponse('Sent')


@login_required(login_url='/login/')
def notificationsV2(request):
    userprofile = request.user.userprofile
    if userprofile.notification_count > 0:
        userprofile.notification_count = 0
        userprofile.save()
    notifications = Notifications.objects.filter(userprofile=userprofile).select_related('userprofile','userprofile__user').order_by('-created_at')
    context = {
        'notifications':notifications,
    }
    return render(request, 'vendroid/notification.html', context)





def forgotPasswordV2(request):
    success_message = None
    form = PasswordResetForm()
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            user = get_object_or_404(User, email__iexact=email)
            pr = PasswordRecover.objects.create(user=user)
            message = "<p class='text-center'>Click the following link to recover your password.</p><br /><br /><a class='btn btn-primary btn-block' href='http://www.yapjoy.com/reset_password/%s/' target='_blank'>Reset Now</a>"%(pr.code)
            send_email(sendTo=email, message=message, title='Dear %s, <br /><br />You or someone pretending to be you have requested a password reset.'%(user.get_full_name()), subject="Password Reset - YapJoy")
            success_message = "Email has been sent to the following email address: %s, Check your email."%(email)
    context = {
        'form':form,
        'success_message':success_message,
    }
    return render(request, 'vendroid/registration/forgot_password.html', context)


def ResetPasswordV2(request, code):
    pr = get_object_or_404(PasswordRecover, code=code, is_recovered=False)
    success_message = None
    error_message = None
    form = Passowrd_reset_form()
    if request.method == "POST":
        form = Passowrd_reset_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            if not email == pr.user.email:
                error_message = 'Enter a valid email address.'
            elif email == pr.user.email:
                user = pr.user
                user.set_password(password)
                user.is_active = True
                user.save()
                pr.is_recovered = True
                pr.save()

                success_message = "Your password has been successfully changed."
        else:
            print 'form is invalid: '
    context = {
        'form':form,
        'success_message':success_message,
        'error_message':error_message,
        'code':code,
    }
    return render(request, 'vendroid/registration/recover_password.html', context)

def send_email_subscribe():
    context={
       'link':'https://www.yapjoy.com/registration/wizard/X12OPLS92JSMAK2123/'
    }
    html_content = render_to_string('vendroid/email/subscription.html', context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives('Smart Wedding Planning Platform', text_content, 'info@yapjoy.com', ['adeelpkpk@gmail.com','wasim@yapjoy.com'])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
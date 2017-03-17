from django.shortcuts import render
from restless.models import serialize
from restless.auth import BasicHttpAuthMixin, login_required
from restless.views import Endpoint
from django.contrib.auth.models import User
from yapjoy_registration.models import UserProfile
from yapjoy_feed.models import *
from yapjoy_registration.models import Friends, AllFriends, optionsSearch, optionsSearch_users, SubscriptionCode, Company
from yapjoy_messages.models import *
from django_comments.models import Comment
from yapjoy_accounts.models import Notifications
from restless.http import Http201, Http404, Http400, HttpError
from django.contrib.auth import authenticate, logout, login
from rest_framework import status
from rest_framework.response import Response
from yapjoy_tasks.models import *
from fullcalendar.util import events_to_json, calendar_options
from django.contrib.auth import authenticate, logout, login as auth_login
from yapjoy_events.models import *
from yapjoy_market.models import *
from yapjoy_forum.models import Forum, Topic
from yapjoy_forum.models import Post as Reply
from django.db.models import Q
import stripe
from yapjoy_accounts.models import CreditPackages, Transaction, TransactionHistory
from yapjoy_registration.commons import check_string_valid

#                for i in 0...jsonData.count {
class Registration(Endpoint):
    response = {}
    def post(self, request):
        try:
            type = request.data.get('type')
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            check = User.objects.filter(email__iexact=email).count()
            if check > 0:
                response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
                return Response(response)
            user = User.objects.create(username=email,email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            userprofile = UserProfile.objects.get(user=user)
            userprofile.type = type
            userprofile.save()
            user_auth = authenticate(username=email, password=password)
            login(request, user_auth)
            # response = {'status':'Success',
            #             'message':'You have registerted successfully.',}
            return Http201(serialize("user is created"))
        except Exception as e:
            print e
            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class Feed(Endpoint):
    response = {}
    def get(self, request):
        try:
            print 'so use',request.user
            # user=User.objects.get(username__iexact=request.user.username)
            feed = Post.objects.filter(user__username__iexact=request.user.username).order_by('-created_at')
            # profile = UserProfile.objects.get(user__username__iexact=request.user.username)
            # dict = {
            #     'feed':feed,
            #     'profile':profile,
            #     'user':user,
            #
            # }
            # return Http201(serialize(dict))


            return serialize(feed, include=[('user',dict(fields=['username','first_name','last_name']))])
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class UserFeed(Endpoint):
    response = {}
    def get(self, request):
        try:
            user = request.user
            print 'so use',request.user
            feed = Post.objects.filter(user_wall_id=user.id).order_by('-created_at')
            return serialize(feed, include=[('user',dict(fields=['username']))])
            # return Http201(serialize(all_causes, include=[('creator', dict(fields=[
            #     'id',
            #     'username',
            #     'first_name',
            #     'last_name',
            #     'email'
            # ]))]))
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class Friends_view(Endpoint):
    response = {}
    def get(self, request):
        try:
            user_friend = Friends.objects.get(user__username__iexact=request.user.username)
            user = request.user
            # user type
            all_friends = filter(lambda x: x != user, user_friend.friends.all())
            print "pre friends", all_friends

            friendsfinal = []
            for f in all_friends:
                fF = Friends.objects.get(user=f)
                #only user side friends
                try:
                    allfriend = AllFriends.objects.get(Q(user=user, friends=fF, type=AllFriends.FRIEND) & ~Q(user=f, friends=user_friend, type=AllFriends.FRIEND))
                    friendsfinal.append(allfriend)
                except:
                    # only friend side friends
                    try:
                        allfriend = AllFriends.objects.get(~Q(user=user, friends=fF, type=AllFriends.FRIEND) & Q(user=f, friends=user_friend, type=AllFriends.FRIEND))
                        friendsfinal.append(allfriend)
                    except:
                        # both sides friends
                        try:
                            allfriend = AllFriends.objects.get(Q(user=user, friends=fF, type=AllFriends.FRIEND) & Q(user=f, friends=user_friend, type=AllFriends.FRIEND))
                            friendsfinal.append(allfriend)
                        except Exception as e:
                            print "both fail", e

            userprofiles = UserProfile.objects.select_related('user').filter(user__in=all_friends).values("user__username","user__first_name","user__last_name","type","image","cover_image")
            #insert the status
            for index, up in enumerate(userprofiles):
                up["status"] = friendsfinal[index].status
                up['allFriendsId'] = friendsfinal[index].id

            print "userprofiles", userprofiles
            return serialize(userprofiles)

        except Exception as e:
            print "friends view wrong", e
            response = []
            return serialize(response)

class Profile(Endpoint):
    response = {}
    def get(self, request):
        try:
            print 'so use',request.user
            feed = UserProfile.objects.get(user__username__iexact=request.user.username)
            return serialize(feed, include=[('user',dict(fields=['username']))])
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class FeedComments(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            comments = Comment.objects.filter(object_pk=id)
            return serialize(comments, include=[('user',dict(fields=['username']))])
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class Inbox(Endpoint):
    response = {}
    def get(self, request):
        try:
            print'in'
            user= request.user
            messages = Message.objects.filter(receiver_id=user.id, receiver_view=True).order_by('-created_at').distinct()
            return serialize(messages, include=[('sender',dict(fields=['username'])),('receiver',dict(fields=['username']))])
            # return Http201(serialize(all_causes, include=[('creator', dict(fields=[
            #     'id',
            #     'username',
            #     'first_name',
            #     'last_name',
            #     'email'
            # ]))]))
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class Outbox(Endpoint):
    response = {}
    def get(self, request):
        try:
            user=request.user
            messages = Message.objects.filter(sender_id=user.id, receiver_read=True, drafted=False).order_by('-created_at')
            return serialize(messages, include=[('sender',dict(fields=['username'])),('receiver',dict(fields=['username']))])
            # return Http201(serialize(all_causes, include=[('creator', dict(fields=[
            #     'id',
            #     'username',
            #     'first_name',
            #     'last_name',
            #     'email'
            # ]))]))
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

class Draft(Endpoint):
    response = {}
    def get(self, request):
        try:
            user = request.user
            messages = Message.objects.filter(sender_id=user.id, drafted=True).order_by('-created_at')
            return serialize(messages, include=[('sender',dict(fields=['username'])),('receiver',dict(fields=['username']))])
            # return Http201(serialize(all_causes, include=[('creator', dict(fields=[
            #     'id',
            #     'username',
            #     'first_name',
            #     'last_name',
            #     'email'
            # ]))]))
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

class Notification(Endpoint):
    response = {}
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user__username__iexact=request.user.username)
            notifi = Notifications.objects.filter(userprofile=profile).values('message','created_at').order_by('-created_at')
            return serialize(notifi)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)



# apiByZaman
class createTask(Endpoint):

    def post(self,request):
        subject = request.data.get('subject',)
        notes = request.data.get('notes')
        assign = request.data.get('assign')
        due = request.data.get('due')
        print 'subject',subject
        print 'notes',notes
        print 'assign',assign
        print 'due',due
        user = User.objects.get(username=request.user.username)
        user_assign = User.objects.get(username=assign)
        print user
        print user.id
        try:
            task = Task.objects.create(
                    user=user,
                    subject=subject,
                    notes=notes,
                    due=due,
                    # assignee=assignee,
                                    )
            print 'task',task.due
            TaskAssign.objects.create(task=task, user_id=user_assign.id)

            return Http201(serialize("user is created"))

        except Exception as e:
            print e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class UpdateUserInfo(Endpoint):

    def post(self,request):
        fName = request.data.get('fName',)
        lName = request.data.get('lName')
        password = request.data.get('password')
        print 'fName',fName
        print 'Lname',lName
        print 'pass',password
        try:
            user = User.objects.get(username=request.user.username)
            user.first_name = fName
            user.last_name = lName
            user.set_password(password)
            user.save()
            print user.first_name
            print user.last_name
            print user.password

            return Http201(serialize("user is created"))

        except Exception as e:
            print e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)


class recommendations(Endpoint):
    response = {}
    def get(self, request):
        WPNUMBER = 30

        user = request.user
        profile = user.userprofile
        suggestions = None
        try:
            if profile.type == "Professional":
                services = list(
                    optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
                if services:
                    subscriptioncodes_ids = SubscriptionCode.objects.filter(is_registered=False).values_list('user_id',
                                                                                                             flat=True)
                    suggestions = UserProfile.objects.select_related('userprofile_company').filter(
                        reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)),
                        ~Q(type__iexact=UserProfile.PROFESSIONAL)).exclude(
                        user__id__in=subscriptioncodes_ids)  # .filter(sub_code__is_registered=True)#.exclude(user=user)
            else:
                services = [x for x in profile.looking_for.split(",") if len(x) > 1]
                print "services", services
                # services = list( optionsSearch_users.objects.filter(userprofile=profile).values_list('open_search__name', flat=True))
                if services:
                    suggestions = UserProfile.objects.filter(
                        reduce(operator.or_, (Q(looking_for__icontains=x) for x in services)),
                        type__iexact=UserProfile.PROFESSIONAL).order_by('-last_seen')[:WPNUMBER].values("user__first_name", "user__last_name", ('image'), ('looking_for'), ('id'))

            print "suggestions", len(suggestions)

            # for s in suggestions:

            return serialize(suggestions)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')

import operator
def get_recommend_users(self, user):
    profile = user.userprofile
    users = None

    return UserProfile.objects.select_related('user').all().exclude(id=profile.id).order_by('-subscribed','-created_at')[:10]

class EventsAll(Endpoint):
    response = {}
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            events_all = CalendarEvent.objects.filter(user=user).values('title', 'start', 'end', 'all_day').order_by('-created_at')
            return serialize(events_all)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)




class EventCreate(Endpoint):
    response = {}
    def post(self,request):
        try:
            user = User.objects.get(username=request.user.username)
            title = request.data.get('title',)
            start = request.data.get('start_date')
            end = request.data.get('end_date')
            all_day = request.data.get('full_day')
            assign = request.data.get('assign')
            print 'title',title
            print 'start',start
            print 'end',end
            print 'assign',assign

            user_assigned = User.objects.get(username=assign)

            tmp_e = CalendarEvent.objects.create(
                        user=user,
                        title=title,
                        start=start,
                        end=end,
                        all_day=all_day,

                        )
            CalendarEventUser.objects.create(user_id=user_assigned.id, calendar_event=tmp_e)
            return Http201(serialize("Event is created"))

        except Exception as e:
            print e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)



class loginUser(Endpoint):
    def post(self,request):
        print 'abcd'
        username = request.data.get('username',)
        password = request.data.get('password')
        print 'ca',username
        print 'ca',password
        user_auth = authenticate(username=username, password=password)
        try:
            print 'auth', user_auth
            user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user_auth)
            print 'auth'
            profile = UserProfile.objects.only("type","image").get(user__username__iexact=username)
            print 'type is', profile.type
            type = profile.type


            return Http201(serialize(profile))
        except Exception as e:
            print e
            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class PostCreate(Endpoint):
    response = {}
    def post(self,request):
        try:
            user = User.objects.get(username=request.user.username)
            post = request.data.get('post',)
            print 'title',post

            postCreate = Post.objects.create(
                        user=user,
                        user_wall=user,
                        text=post,

                        )
            return Http201(serialize("Post is created"))

        except Exception as e:
            print e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class UserFriendFeed(Endpoint):
    response = {}
    def get(self, request,username):
        try:
            print username
            user = User.objects.get(username__iexact=username)
            feed = Post.objects.filter(user_wall_id=user.id).order_by('-created_at')
            print feed
            return serialize(feed, include=[('user',dict(fields=['username']))])
            # return Http201(serialize(all_causes, include=[('creator', dict(fields=[
            #     'id',
            #     'username',
            #     'first_name',
            #     'last_name',
            #     'email'
            # ]))]))
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize('Failed')




class FeedLike(Endpoint):
    def post(self,request):
        print 'abcd'
        id = request.data.get('id',)

        print 'ca',id
        post = Post.objects.get(id=id)
        try:

            print 'in try'

            postLiked= PostLike.objects.filter(user=request.user,statuspost=post)
            if postLiked:
                response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
                return Response(response)
            else:

                PostLike.objects.create(user=request.user,
                                        statuspost=post,
                                        )
                post.likes_count += 1
                post.save()
                print 'save'
                return Http201(serialize("like"))

        except Exception as e:
            print e
            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)
class Logout(Endpoint):
    def post(self, request):
        try:
            print 'usrr',request.user
            logout(request)
            return {'Result':'Ok'}
        except:
            return {'Result':'Error:'}
            # Create your views here.


class DeletePost(Endpoint):
    def post(self, request):
        id = request.data.get('id',)
        print 'iddel',id
        post = Post.objects.get(id=id)

        if post.user == request.user or post.user_wall == request.user:
            post.delete()
            print 'deleted'
            return Http201(serialize("Deleted"))
        else:
            print 'in else'
            response = {
                    'transaction':'failed',
                    'description':'You can only delete your own posts.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class PostComment(Endpoint):
    response = {}
    def post(self,request):
        try:
            user = User.objects.get(username=request.user.username)
            id = request.data.get('id')
            post = request.data.get('post')
            print 'id',id
            print 'id',post
            print 'id',user.username

            # Comment = apps.get_model('django_comments', 'Comment')
            comment = Comment.objects.create(
                        user=user,
                        user_name=user.username,
                        user_email=user.email,
                        comment=post,
                        object_pk=id,
                        content_type_id=1,
                        site_id=1,

                        )
            return Http201(serialize("Comment is created"))

        except Exception as e:
            print e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)



class TasksUser(Endpoint):
    response = {}
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            # user = User.objects.get(id=1)
            tasks_all = Task.objects.filter(user=user).exclude(complete=True).distinct().order_by('due')
            return serialize(tasks_all)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

class PlansUser(Endpoint):
    response = {}
    def get(self, request):
        try:
            user = User.objects.get(username=request.user.username)
            # user = User.objects.get(id=10677)
            products = Product.objects.filter(user=user).select_related('user').order_by('created_at')
            return serialize(products)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

from yapjoy_files.models import Event_fairs
class Events(Endpoint):
    response = {}
    def get(self, request):
        try:

            events = Event_fairs.objects.all()
            return serialize(events)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

class PlansDetail(Endpoint):
    response = {}
    def get(self, request,id):
        try:
            products = Product.objects.get(id=id)
            return serialize(products)
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)


class forums(Endpoint):
    def get(self, request):
        try:
            forums = Forum.objects.all()

            response = []
            for f in forums:
                resp = {
                    "id": f.id,
                    "title": f.title,
                    "num_posts": int(f.num_posts())
                }
                response.append(resp)

            print "forum response", response

            return serialize(response)

        except Exception as e:
            print "forum response fail", e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

class forumTopics(Endpoint):
    def get(self, request, id):
        try:
            topics = Topic.objects.filter(forum=id).select_related('forum').order_by("-created")

            response = []
            for f in topics:
                try: url = f.picture.url
                except: url = ""

                # print "f.picture.url", url
                resp = {
                    "id": f.id,
                    "title": f.title,
                    "description": f.description,
                    "num_posts": int(f.num_posts()),
                    "imageUrl": url
                }
                response.append(resp)

            print "topic response", response

            return serialize(response)
        except Exception as e:
            print "topic response fail", e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

class forumCreateReply(Endpoint):
    def post(self, request):
        try:
            topicId = request.data.get('topicid')
            userProfileId = request.data.get('upid')
            replyBody = request.data.get('text')

            Reply.objects.create(topic_id=topicId, creator_id=userProfileId, body=replyBody)
            return serialize("success")

        except Exception as e:
            print "topic response fail", e
            response = {'status':'failed',
                        'message':e}
            return Http400(response)

class forumCreateTopic(Endpoint):
    response = {}
    def post(self, request):
        try:
            forumId = request.data.get('forumId')
            upId = request.data.get('upId')
            title = request.data.get('title')
            description = request.data.get('description')
            imageUrl = request.data.get('imageUrl')

            # print "forumId, ", forumId
            # print "title, ", title
            # print "description ", description
            # print "imageUrl ", imageUrl
            # print "upId ", upId

            userId = UserProfile.objects.select_related("user__id").get(id=upId).user.id
            # print "userId ", userId



            #Fix me----create a imageUrl field in Topic
            #due to saving image failed from iOS to database
            Topic.objects.create(forum_id=forumId, creator_id=userId, title=title, description=description, picture=imageUrl)

            return serialize("success")

        except Exception as e:
            print "topic response fail", e
            response = {'status':'failed',
                        'message':e,}
            return Http400(response)


class deletePlan(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            Product.objects.get(pk=id, status=Product.ACTIVE).delete()

            return serialize("success")
        except Exception as e:
            print "delete plan failed"
            response = {'status': 'failed',
                        'message': e,}
            return Http400(response)

class addPlan(Endpoint):
    response = {}
    def post(self, request):
        try:
            planId = request.data.get("planId")
            upId = request.data.get("upId")
            title = request.data.get("title")
            description = request.data.get("description")
            category = request.data.get("category")
            enddate = request.data.get("enddate")
            amount = int(request.data.get("amount"))


            try:
                plan = Product.objects.get(pk=planId)
                plan.title = title
                plan.description = description
                # plan.category = category
                # plan.end_date = enddate   #fix me??
                plan.amount = amount
                plan.save()
                print " edit product success"
                return serialize("success")

            except:
                print "try create product"
                userId = UserProfile.objects.select_related("user__id").get(id=upId).user.id

                print "user id", userId
                plan = Product.objects.create(user_id=userId,
                                              title=title,
                                              description=description,
                                              # category=category,
                                              amount=amount,
                                              # enddate=enddate #fix me
                                              )

                return serialize("success")

        except Exception as e:
            print "add plan failed", e
            response = {'status': 'failed',
                        'message': e,}
            return Http400(response)


class getBid(Endpoint):
    response = {}
    def post(self, request):
        try:
            planId = request.data.get("planid")

            response = Pledge.objects.filter(product__id=planId).values("id", "user__first_name", "user__last_name", "modified_at", "amount", "message", "is_awarded", "created_at")
            print "get bids", response

            return serialize(response)

        except Exception as e:
            print e

            response = []
            return serialize(response)

class acceptBid(Endpoint):
    response = {}
    def post(self, request):
        try:
            planId = request.data.get("planId")
            bidId = request.data.get("bidId")
            print "plan id and bid id", planId, bidId

            pledge = Pledge.objects.get(pk=bidId)
            pledge.is_awarded = True
            pledge.save()
            print "pledge awarded"

            plan = Product.objects.get(pk=planId)
            plan.awarded_to = pledge
            plan.is_completed = True
            plan.save()
            print "product awarded"

            return serialize("success")

        except Exception as e:
            print "accept bid failed"
            response = {'status': 'failed',
                        'message': e,}
            return Http400(response)

class getWpProfile(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            # print id
            up = UserProfile.objects.get(id=id)
            user = up.user

            address = ""
            try:
                if len(up.city) > 1:
                    address = up.city
                    if len(up.state) > 1:
                        address += ", "+ up.state
                else:
                    if len(up.state) > 1:
                        address = up.state
            except:
                address = ""

            if up.looking_for == None: type = "Everything"
            else: type = up.looking_for

            try:
                cp = Company.objects.get(userprofile=up)
                # print "cp", cp.name
                if cp.name == None:
                    cp_name = ""
                else:
                    cp_name = cp.name

                response = {
                    "id": up.id,
                    "name": user.get_full_name(),
                    "type": type,
                    "image": str(up.image),
                    "cover_image": str(up.cover_image),
                    "phone": up.phone,
                    "address": address,
                    "employees": cp.employees,
                    "companyName": cp_name,
                    "bids": up.bids_count,
                    "viewCnt": up.views_count,
                    "email": user.email
                }
            except:
                response = {
                    "id": up.id,
                    "name": user.get_full_name(),
                    "type": type,
                    "image": str(up.image),
                    "cover_image": str(up.cover_image),
                    "phone": up.phone,
                    "address": address,
                    "employees": "",
                    "companyName": "",
                    "bids": up.bids_count,
                    "viewCnt": up.views_count,
                    "email": user.email
                }

            print "wp profile success", response

            return serialize(response)
        except Exception as e:
            print "wp profile fail", e

            response = {'status':'failed',
                        'message':e
                        }

            return Http400(response)


class summary(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            up = UserProfile.objects.select_related('user').get(id=id)
            user = up.user

            eventCnt = CalendarEvent.objects.filter(user=request.user).count()
            taskCnt = Task.objects.filter(user=user, complete=False).count()

            if up.type == UserProfile.PROFESSIONAL:
                followerCnt = AllFriends.objects.filter(user=user, status=AllFriends.FOLLWOING).count()
                bids = Pledge.objects.filter(user=user)
                bidCnt = bids.count()
                awardCnt = bids.exclude(is_awarded=False).count()
                # awardCnt = Pledge.objects.filter(user=user, is_awarded=True).count()

                response = {
                    "followerCnt": followerCnt,
                    "eventCnt": eventCnt,
                    "taskCnt": taskCnt,
                    "bidCnt": bidCnt,
                    "awardCnt": awardCnt
                }
            else:
                productCnt = Product.objects.filter(user=user).count()
                weddingDate = "" if up.wedding_date == None else str(up.wedding_date)
                response = {
                    "weddingDate": weddingDate,
                    "eventCnt": eventCnt,
                    "taskCnt": taskCnt,
                    "productCnt": productCnt
                }

            print "summary success", response

            return serialize(response)
        except Exception as e:
            print "summary fail", e

            response = {'status':'failed',
                        'message':e
                        }

            return Http400(response)


# class friends(Endpoint):
#     user = request.user
#     success_message = None
#     if request.method == 'POST':
#         if "accept" in request.POST or "reject" in request.POST:
#             if 'accept' in request.POST:
#                 accept = request.POST.get('accept')
#                 objF = get_object_or_404(AllFriends,id=accept)
#                 objF.status = AllFriends.ACCEPTED
#                 objF.save()
#                 Notifications.objects.create(userprofile=objF.friends.user.userprofile, message="%s has accepted your friends request."%(objF.user.get_full_name()))
#                 send_email(objF.friends.user.email, message="%s has accepted your friends request."%(objF.user.get_full_name()), title="Friends request accepted", subject="Your friends request has been accepted on Yapjoy")
#             if 'reject' in request.POST:
#                 reject = request.POST.get('reject')
#                 objF = get_object_or_404(AllFriends,id=reject).delete()
#
#         elif "emails" in request.POST:
#             print "in emails"
#             emails = request.POST.get('emails')
#             emails = emails.split(',')
#             for email in emails:
#                 friends = None
#                 try:
#                     friends = Friends.objects.get(user=user)
#                 except:
#                     friends = Friends.objects.create(user=user)
#                 try:
#                     user_offer = User.objects.get(username__iexact=email)
#                     AllFriends.objects.get_or_create(friends=friends, user=user_offer)
#                 except:
#                     print "Sending email to: ",email.strip()
#                     user_new = None
#                    # if re.match(r"^[a-zA-Z0-9._]+\@[a-zA-Z0-9._]+\.[a-zA-Z]{3,}$", email.strip()):
#                     try:
#                         print "invited_%s"%(email.strip())
#                         user_new = User.objects.get_or_create(username="invited_%s"%(email.strip()), email="invited_%s"%(email.strip()))
#                         AllFriends.objects.get_or_create(friends=friends, user=user_new[0], status=AllFriends.INVITED)
#                     except Exception as e:
#                         print e
#                         return HttpResponseRedirect('')
#                     context = {
#                         'link':"https://www.yapjoy.com/invitation/accept/%s"%(user_new[0].email),
#                         'name':request.user.get_full_name()
#                     }
#                     html_content = render_to_string('email/invite.html', context)
#                     text_content = strip_tags(html_content)
#                     msg = EmailMultiAlternatives('YapJoy Invitation by %s'%(request.user.email), text_content, 'info@yapjoy.com', [email])
#                     msg.attach_alternative(html_content, "text/html")
#                     msg.send()
#                     success_message = "You have successfully sent the invitation."
#                     print 'email is sent'
#
#     all_friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile')
#     followings = AllFriends.objects.filter(friends__user=user, type=AllFriends.PROFESSIONAL)
#     social_post_facebook_connected = None
#
#     context = {
#         'all_friends':all_friends,
#         'followings':followings,
#         'user':user,
#         'success_message': success_message,
#     }
#     return render(request, 'vendroid/iFrame/friends.html', context)

class unfriend(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            user = request.user
            userFriend = Friends.objects.get(user=user)

            # only user side friends
            try:
                allfriend = AllFriends.objects.get(id=id, user=user, type=AllFriends.FRIEND)
                target = allfriend.friends
                allfriend.delete()
                print "get A", target

                #try to delete the other side around
                try:
                    allfriend = AllFriends.objects.get(user=target.user, friends=userFriend, type=AllFriends.FRIEND)
                    allfriend.delete()
                except Exception as e:
                    print "delete A", e
                    pass

            except Exception as e:
                print "get B", e

                # only friend side friends
                try:
                    allfriend = AllFriends.objects.get(id=id, friends=userFriend, type=AllFriends.FRIEND)
                    target = Friends.objects.get(user=allfriend.user)
                    allfriend.delete()

                    # try to delete the other side around
                    try:
                        allfriend = AllFriends.objects.get(user=user, friends=target, type=AllFriends.FRIEND)
                        allfriend.delete()
                    except Exception as e:
                        print "delete B", e
                        pass

                except Exception as e:
                    print "get C", e
                    target = []

            # Notifications.objects.create(userprofile=target.user.userprofile, message="%s has rejected your friends request." % (user.get_full_name()))
            send_email(target.user.email, message="%s has rejected your friends request." % (user.get_full_name()),
                       title="Friends request rejected", subject="Your friends request has been rejected on Yapjoy")

            return serialize("success")

        except Exception as e:
            print "unfriend wrong", e

            return Http400('Failed')

class acceptfriend(Endpoint):
    response = {}
    def get(self, request, id):
        try:
            user = request.user
            userFriend = Friends.objects.get(user=user)

            # only user side friends
            try:
                allfriend = AllFriends.objects.get(id=id, user=user, type=AllFriends.FRIEND)
                target = allfriend.friends
                print "get A", target

                allfriend.status = AllFriends.ACCEPTED
                allfriend.save()

                try:
                    allfriend = AllFriends.objects.get(user=target.user, friends=userFriend, type=AllFriends.FRIEND)
                    allfriend.status = AllFriends.ACCEPTED
                    allfriend.save()
                except Exception as e:
                    print "accept A", e
                    AllFriends.objects.create(user=target.user, friends=userFriend, type=AllFriends.FRIEND, status=AllFriends.ACCEPTED)

            except Exception as e:
                print "get B", e
                # only friend side friends
                try:
                    allfriend = AllFriends.objects.get(id=id, friends=userFriend, type=AllFriends.FRIEND)
                    target = Friends.objects.get(user=allfriend.user)

                    allfriend.status = AllFriends.ACCEPTED
                    allfriend.save()

                    try:
                        allfriend = AllFriends.objects.get(user=user, friends=target, type=AllFriends.FRIEND)
                        allfriend.status = AllFriends.ACCEPTED
                        allfriend.save()
                    except Exception as e:
                        print "accept C", e
                        AllFriends.objects.create(user=user, friends=target, type=AllFriends.FRIEND, status=AllFriends.ACCEPTED)

                except Exception as e:
                    print "accept D",e
                    target = []

            print("send to email", target.user.email)
            # Notifications.objects.create(userprofile=target.user.userprofile, message="%s has accepted your friends request." % (user.get_full_name()))
            send_email(target.user.email, message="%s has accepted your friends request."%(user.get_full_name()),
                       title="Friends request accepted", subject="Your friends request has been accepted on Yapjoy")

            return serialize("success")

        except Exception as e:
            print "accept friend wrong", e

            return Http400('Failed')


class creditcharge(Endpoint):
    def post(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            user = request.user
            userprofile = user.userprofile
            token = request.data.get("stripeToken")
            # print "user", user
            # print "token", token
            print "api key", stripe.api_key

            try:
                """
                Already has stripe id
                """
                print "try get id"
                tmp = userprofile.stripe_id

                if check_string_valid(tmp):
                    u_stripeid = tmp
                else:
                    stripe_customer = stripe.Customer.create(
                        email=user.email,
                        source=token,
                        description=user.email
                    )
                    u_stripeid = stripe_customer.id
                    userprofile.stripe_id = u_stripeid
                    userprofile.save()

                print "id", u_stripeid
            except:
                """
                New stripe customer
                """
                print "email", user.email
                print "token", token

                stripe_customer = stripe.Customer.create(
                    email = user.email,
                    source = token,
                    description = user.email
                )

                print "stripe id", stripe_customer.id
                u_stripeid = stripe_customer.id
                userprofile.stripe_id = u_stripeid
                userprofile.save()

            """
            Charge/transaction
            """
            try:
                print "charging...."

                amount = int(str(30))
                stripe.api_key = settings.STRIPE_SECRET_KEY
                response = stripe.Charge.create(
                    amount=int(100) * amount,  # Convert dollars into cents
                    currency="usd",
                    customer=u_stripeid,
                    description=user.email,
                )
                print "response.....", response

                if response:
                    print 'PAYMENT DONE'
                    Transaction.objects.create(user=user, amount=str(30), status=Transaction.COMPLETED,
                                               response=response, transaction_id=response['balance_transaction'])
                    TransactionHistory.objects.create(user=user, event="Subscription Purchased.",
                                                      amount=int(str(amount)))

                    userprofile.subscribed = True
                    userprofile.amount += 30
                    userprofile.save()
                    # successMessage = "$10 Subscription has been successfully activated."

                return serialize("success")

            except Exception as e:
                print 'transaction error:', e
                return Http400("failed")

        except Exception as e:
            print 'post error:', e
            return Http400("post error")


class products(Endpoint):
    def get(self, request):
        try:
            products = Product.objects.filter(is_completed=False, status="Active").select_related('user').order_by('created_at')
            presp = products.values('id', 'user__username', 'category', 'title', 'description', 'amount', 'end_date', 'status')

            response = []
            bidsNoAry = []
            i = 0
            for p in products:
                # print p.title
                try:
                    bidNo = Pledge.objects.filter(product=p).count()
                except:
                    bidNo = 0
                bidsNoAry.append(str(bidNo))

            # print bidsNoAry
            for p in presp:
                p['bidNo'] = bidsNoAry[i]

                try:
                    p['end_date'] = str(p['end_date'])

                    if p['end_date'] == "None":
                        p['end_date'] = ""
                except:
                    p['end_date'] = ""

                # print p
                response.append(p)
                i += 1

            # print "products", len(response)
            return serialize(response)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)


class addbid(Endpoint):
    response = {}
    def post(self, request):
        try:
            productId = request.data.get('productId')
            bidDesp = request.data.get('bidDesp')
            bidAmount = request.data.get('bidAmount')

            amount = int(bidAmount)
            msg = str(bidDesp)
            print amount, msg

            # user = User.objects.get(user__username__iexact=request.user.username)
            pledge = Pledge.objects.create(user_id=request.user.id, product_id=productId, amount=amount, message=msg, is_awarded=False)
            print "pledge", pledge

            return serialize("success")

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)


class updatecategory(Endpoint):
    response = {}
    def post(self, request):
        try:
            category = request.data.get('category')
            # print category

            # cates = category.replace(",", " ")
            # print cates

            up = UserProfile.objects.get(user_id=request.user.id)
            up.looking_for = category
            up.save()

            return serialize("success")

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)


class following(Endpoint):
    response = {}
    def post(self, request):
        try:
            id = request.data.get("id")
            type = request.data.get("type")
            user = request.user
            wp = UserProfile.objects.select_related("user").filter(id=id)[0].user
            # print id, type, user, wp

            try:
                friends = Friends.objects.get(user=user)
            except Exception as e:
                print "Friends exception: ", e
                friends = Friends.objects.create(user=user)

            try:
                allfriends = AllFriends.objects.filter(user=wp, friends__user_id=user, type=AllFriends.PROFESSIONAL, status=AllFriends.FOLLWOING)
                if allfriends.count() > 0: is_following = True
                else: is_following = False
            except Exception as e:
                print "not folloing", e
                is_following = False

            print "is_following", is_following
            if not is_following and type == "follow":
                try:
                    friend_to_add = AllFriends.objects.create(user=wp, friends=friends, type=AllFriends.PROFESSIONAL,
                                                              status=AllFriends.FOLLWOING)
                    print "following success"
                except Exception as e:
                    print "follow All friends exception: ", e

            if is_following and type == "unfollow":
                try:
                    friend_to_add = AllFriends.objects.filter(user=wp, friends=friends, type=AllFriends.PROFESSIONAL,
                                                          status=AllFriends.FOLLWOING).delete()
                    print "unfollowing success"
                except Exception as e:
                    print "unfollow All friends exception: ", e

            print "success"
            return serialize("success")

        except Exception as e:
            print "following at the end", e
            response = {'status': 'failed',
                        'message': e,}
            return serialize(response)


class registerinfo(Endpoint):
    def post(self,request):
        category = request.data.get('category',)
        weddingDate = request.data.get('weddingDate')
        street = request.data.get('street')
        city = request.data.get('city')
        state = request.data.get('state')
        zip = request.data.get('zip')

        print 'category', category
        print 'weddingDate', weddingDate

        try:
            up = UserProfile.objects.get(user=request.user)
            up.looking_for = category
            up.wedding_date = weddingDate
            up.street = street
            up.city = city
            up.state = state
            up.zip = zip
            up.save()

            print "success"
            return serialize("success")

        except Exception as e:
            print "fail", e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)



class updateaddress(Endpoint):
    def post(self,request):
        street, city, state, zip = request.data.get('address').split(",")
        print 'street', street, city, state, zip

        try:
            up = UserProfile.objects.get(user=request.user)
            up.street = street
            up.city = city
            up.state = state
            up.zip = zip
            up.save()

            print "success"
            return serialize("success")

        except Exception as e:
            print "fail", e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)

class updateweddingdate(Endpoint):
    def post(self,request):
        weddingDate = request.data.get('weddingDate')
        print 'weddingDate', weddingDate

        try:
            up = UserProfile.objects.get(user=request.user)
            up.wedding_date = weddingDate
            up.save()

            print "success"
            return serialize("success")

        except Exception as e:
            print "fail", e

            response = {
                    'transaction':'failed',
                    'description':'Your request cannot be processed, as the location is not active anymore.',
                    'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            return Response(response)


class getprofileinfo(Endpoint):
    def get(self, request):
        try:
            up = UserProfile.objects.get(user=request.user)
            addressAry = [up.street, up.city, up.state, up.zip, ""]
            addr = reduce(lambda x,y: x+","+y, filter(lambda x: x != None, addressAry))

            looking_for = "" if up.looking_for == None else up.looking_for
            wedding_date = "" if up.wedding_date == None else up.wedding_date
            print "addr", addr

            response = {
                "firstName": up.user.first_name,
                "lastName": up.user.last_name,
                "category": looking_for,
                "weddingDate": wedding_date,
                "address": addr
            }

            print "success", response
            return serialize(response)

        except Exception as e:
            print " register user failed", e

            return Http400("failed")


from yapjoy_files.models import Event_fairs, Register_Event, Register_Event_Interested
class Events(Endpoint):
    response = {}
    def get(self, request):
        try:

            events = Event_fairs.objects.all().order_by('-date')
            return serialize(events)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)

from yapjoy_files.models import Event_fairs
from django.db.models import Q
class AutocompleteVendorsInterested(Endpoint):
    response = {}
    def get(self, request):
        try:
            search = request.GET.get('term')
            print search
            vendors = Register_Event_Interested.objects.filter(Q(name__icontains=search)|Q(business_name__icontains=search)|Q(email__icontains=search)).distinct('user_id')#.values_list('user__email', flat=True
                                                                                                                                             # ,'name','business_name'
                                                                                                                                             # )
            print vendors
            ven_list = []
            for ven in vendors:
                ven_list.append('%s (%s, %s)'%(ven.email, ven.name, ven.business_name))
            return serialize(ven_list)
            return serialize(vendors)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)[0]

class AutocompleteVendors(Endpoint):
    response = {}
    def get(self, request):
        try:
            search = request.GET.get('term')
            print search
            vendors = Register_Event.objects.filter(Q(name__icontains=search)|Q(business_name__icontains=search)|Q(email__icontains=search)).distinct('user_id')#.values_list('user__email', flat=True
                                                                                                                                             # ,'name','business_name'
                                                                                                                                             # )
            print vendors
            ven_list = []
            for ven in vendors:
                ven_list.append('%s (%s, %s)'%(ven.email, ven.name, ven.business_name))
            return serialize(ven_list)
            return serialize(vendors)

        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)[0]

class PlansDetail(Endpoint):
    response = {}
    def get(self, request,id):
        try:
            products = Product.objects.get(id=id)
            return serialize(products)
        except Exception as e:
            print e
            response = {'status':'failed',
                        'message':e,}
            return serialize(response)



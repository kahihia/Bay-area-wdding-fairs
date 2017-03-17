from django.shortcuts import render, HttpResponseRedirect, Http404
from django.http import HttpResponse, Http404
from yapjoy_registration.models import Friends
from django.contrib.auth.decorators import login_required
from .forms import messageForm
from django.db.models import Q
from .models import *
from yapjoy_registration.models import AllFriends


@login_required(login_url='/login/')
def messages(request):
    user = request.user
    profile = user.userprofile
    if profile.message_count > 0:
        profile.message_count = 0
        profile.save()
    messages = Message.objects.filter(receiver=user, receiver_view=True, drafted=False).order_by('-created_at')
    content = {
        'messages':messages
    }
    return render(request, 'vendroid/messages/messages.html', content)

def messages_sent(request):
    user = request.user
    messages = Message.objects.filter(sender=user, sender_view=True, drafted=False).order_by('-created_at')
    content = {
        'messages':messages
    }
    return render(request, 'vendroid/messages/sent.html', content)

def messages_draft(request):
    user = request.user
    drafts = Message.objects.filter(sender=user, drafted=True).order_by('-created_at')
    content = {
        'drafts':drafts
    }
    return render(request, 'vendroid/messages/draft.html', content)

def messages_draft_edit(request, id):
    user = request.user
    draft = None
    print 'working draft edit'
    try:
        draft = Message.objects.get(id=id, sender=request.user)
    except:
        raise Http404
    form = messageForm(initial = {'message':draft.message,
                                  'subject':draft.subject,
                                  })
    if request.method == "POST":
        form = messageForm(request.POST)
        if form.is_valid():
            print 'inside clean'
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            print subject, message
            draft.subject = subject
            draft.message = message
            draft.drafted = False
            draft.save()
            return HttpResponseRedirect('/messages/')
    content = {
        'form':form,
        'draft':draft,
    }
    return render(request, 'vendroid/messages/drafted.html', content)

def messages_view(request, id):
    user = request.user
    message = Message.objects.get(id=id)
    conversation = Message.objects.filter(Q(sender=message.sender, receiver=user)|Q(sender=user, receiver=message.sender)).order_by('created_at')

    if message.receiver_read == False:
        message.receiver_read = True
        message.save()
    form = messageForm()
    if request.method == "POST":
        message_rep = request.POST.get('message')
        Message.objects.create(sender=user, receiver_id=message.sender.id, subject="RE: %s"%(message.subject), message=message_rep)
    content = {
        'message':message,
        'form':form,
        'user':user,
        'conversation':conversation,
    }

    # if request.POST.get('inbox_detail'):
    template_name = 'vendroid/messages/detail.html'
    # if request.POST.get('sent_detail'):
    #     print("sent detail calling")
    #     template_name = 'vendroid/messages/sent_detail.html'

    return render(request, template_name, content)

def messages_sent_view(request, id):
    user = request.user
    message = Message.objects.get(id=id)
    conversation = Message.objects.filter(Q(sender=message.sender, receiver=user)|Q(sender=user, receiver=message.sender)).order_by('created_at')
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')#.values('user','friends','friends__user')
    if message.receiver_read == False:
        message.receiver_read = True
        message.save()
    form = messageForm()
    if request.method == "POST":
        message_rep = request.POST.get('message')
        Message.objects.create(sender=user, receiver_id=message.sender.id, subject="RE: %s"%(message.subject), message=message_rep)
    content = {
        'message':message,
        'form':form,
        'friends':friends,
        'conversation':conversation,
    }
    return render(request, 'vendroid/messages/sent_detail.html', content)

@login_required(login_url='/login/')
def messages_compose(request):
    user = request.user
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')#.values('user','friends','friends__user')
    #print friends
    form = messageForm()
    if request.method == "POST":
        form = messageForm(request.POST)
        if form.is_valid():
            to_users = request.POST.get('to_users')
            draft = request.POST.get('draft')
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            print subject, message
            print 'to_users',to_users
            if draft == "1":
                Message.objects.create(sender=user, receiver_id=to_users, subject=subject, message=message, drafted=True)
            else:
                Message.objects.create(sender=user, receiver_id=to_users, subject=subject, message=message)
            return HttpResponseRedirect('/messages/')

    content = {
        'friends':friends,
        'form':form,
    }
    # return render(request, 'messages/compose.html', content)
    return render(request, 'vendroid/messages/compose.html', content)

@login_required(login_url='/loginv2/')
def messagesV2(request):
    user = request.user
    profile = user.userprofile
    if profile.message_count > 0:
        profile.message_count = 0
        profile.save()
    messages = Message.objects.filter(receiver=user, receiver_view=True, drafted=False).order_by('-created_at')
    content = {
        'messages':messages
    }
    return render(request, 'vendroid/messages/messages.html', content)

@login_required(login_url='/loginv2/')
def messages_composeV2(request):
    print 'came'
    user = request.user
    print 'us',user
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')#.values('user','friends','friends__user')
    #print friends
    form = messageForm()
    if request.method == "POST":
        form = messageForm(request.POST)
        if form.is_valid():
            to_users = request.POST.get('to_users')
            draft = request.POST.get('draft')
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            print subject, message,draft
            print 'to_users',to_users
            if draft == "1":
                Message.objects.create(sender=user, receiver_id=to_users, subject=subject, message=message, drafted=True)
            else:
                Message.objects.create(sender=user, receiver_id=to_users, subject=subject, message=message)
            return HttpResponseRedirect('/messagesv2/')

    content = {
        'friends':friends,
        'form':form,
    }
    return render(request, 'vendroid/messages/compose.html', content)



def messages_sentV2(request):
    user = request.user
    messages = Message.objects.filter(sender=user, sender_view=True, drafted=False).order_by('-created_at')
    content = {
        'messages':messages
    }
    return render(request, 'vendroid/messages/sent.html', content)

def messages_draftV2(request):
    user = request.user
    drafts = Message.objects.filter(sender=user, drafted=True).order_by('-created_at')
    content = {
        'drafts':drafts
    }
    return render(request, 'vendroid/messages/draft.html', content)


def messages_draft_editV2(request, id):
    user = request.user
    draft = None
    print 'working draft edit'
    try:
        draft = Message.objects.get(id=id, sender=request.user)
    except:
        raise Http404
    form = messageForm(initial = {'message':draft.message,
                                  'subject':draft.subject,
                                  })
    if request.method == "POST":
        form = messageForm(request.POST)
        if form.is_valid():
            print 'inside clean'
            data = form.cleaned_data
            subject = data['subject']
            message = data['message']
            print subject, message
            draft.subject = subject
            draft.message = message
            draft.drafted = False
            draft.save()
            return HttpResponseRedirect('/messagesv2/')
    content = {
        'form':form,
        'draft':draft,
    }
    return render(request, 'vendroid/messages/drafted.html', content)

# new messages features
# for request without csrf token need to add exempt
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# @login_required(login_url='/login/')
# @csrf_exempt
# def online_message(request):
#     user = request.user
#     form = messageForm()
#
#     #remove red alert in the header
#     profile = user.userprofile
#     if profile.message_count > 0:
#         profile.message_count = 0
#         profile.save()
#
#     #(1)show up the 1st friend's conversation as default######
#     try:
#         all_friends = AllFriends.objects.filter(Q(Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile').order_by('created_at')
#         followings = AllFriends.objects.filter(friends__user=user, type=AllFriends.PROFESSIONAL)
#         default_sender = all_friends[0].friends.user
#         form_sender_id = default_sender.id
#         conversation = Message.objects.filter((Q(sender=default_sender, receiver=user)) | (Q(sender=user, receiver=default_sender))).order_by('created_at')
#     except:
#         #if no friends found out.
#         content = {
#             'user':user,
#             'form':form,
#         }
#         return render(request, 'vendroid/messages/online_message.html', content)
#
#
#     #(2)show up conversation based on friends######
#     if request.is_ajax() and "find_friend_message" in request.POST:
#         # print "find_friend_message happens"
#         friend_user_id = request.POST.get('find_friend_message')
#         # print friend_user_id
#         if friend_user_id:
#             friend_query = User.objects.filter(Q(id=friend_user_id))
#             friends_tmp = AllFriends.objects.filter(Q(friends__user=friend_query))
#             friends_send = friends_tmp[0].friends.user
#             print friends_send.get_full_name
#
#             form_sender_id = friend_user_id
#             conversation = Message.objects.filter(Q(sender=friend_query, receiver=user)|Q(sender=user, receiver=friend_query)).order_by('created_at')
#
#             #by only rendering conversation.html page here,
#             # it will be replaced according to different friends
#             content = {
#                 'user':user,
#                 'friend':friends_send,
#                 'conversation':conversation,
#             }
#             return render(request, "vendroid/messages/conversation.html", content)
#
#     #(3)Compose the Message######
#     # print form_sender.get_full_name()
#     if request.method == "POST":
#         form = messageForm(request.POST)
#         # form.subject = "dummy"
#         # print form.subject
#         if form.is_valid():
#             print "is valid"
#             # to_users = request.POST.get('to_users')
#             # draft = request.POST.get('draft')
#             data = form.cleaned_data
#             # subject = data['subject']
#             message = data['message']
#             # print subject, message
#             # print 'to_users'to_users
#
#             # Message.objects.create(sender=user, receiver_id=to_users, subject=subject, message=message)
#             Message.objects.create(sender=user, receiver_id=form_sender_id, message=message)
#             return HttpResponseRedirect('/online_message/')
#
#     content = {
#         # 'message':message,
#         'user':user,
#         'form':form,
#         'conversation':conversation,
#         'all_friends':all_friends,
#         'friend':default_sender,
#         # 'followings':followings,
#     }
#
#     template_name = 'vendroid/messages/online_message.html'
#
#     return render(request, template_name, content)

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, loader
from restless.models import serialize
from django.core import serializers
import json
@login_required(login_url='/login/')
@csrf_exempt
def online_message(request):
    user = request.user
    form = messageForm()
    unread_messages = []
    deduct = False
    unknown_messages = None
    #remove red alert in the header
    profile = user.userprofile
    if profile.message_count > 0:
        profile.message_count = 0
        profile.save()

    #(1)show up the 1st friend's conversation as default######
    try:
        # all_friends = AllFriends.objects.filter(Q(Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile').order_by('created_at')

        #for professional/vendor
        if user.userprofile.type == AllFriends.PROFESSIONAL:
            try:
                all_friends = AllFriends.objects.filter(Q(Q(user=user)|Q(friends__user=user))).filter(Q(status=AllFriends.FOLLWOING))
            except:
                pass
        #for user groom/bride
        else:
            all_friends = AllFriends.objects.filter(Q(Q(user=user)|Q(friends__user=user))).filter(Q(Q(status=AllFriends.ACCEPTED)|Q(status=AllFriends.FOLLWOING))).select_related('user','user__userprofile').order_by('created_at')
        all_friends_user_id = all_friends.values_list('user_id', flat=True)
        all_friends_user_friends_id = all_friends.values_list('friends__user_id', flat=True)
        unknown_messages = Message.objects.filter(receiver=request.user).exclude(Q(sender__in=all_friends_user_id)|Q(sender__in=all_friends_user_friends_id)).distinct('sender')
        print "Unknown messages: ",unknown_messages.count()
        unread_messages_unknown = []
        for friend in unknown_messages:
            try:
                # print friend.friends.user.get_full_name()
                temp_num = Message.objects.filter(Q(sender=friend.sender, receiver=request.user, receiver_read=False)).count()
            except:
                temp_num = 0

            # print "temp_num is "+str(temp_num)
            temp_num = int(temp_num)
            unread_messages_unknown.append(temp_num)
        default_sender = None
        form_sender_id = None
        conversation = None
        # followings = AllFriends.objects.filter(friends__user=user, type=AllFriends.PROFESSIONAL)
        if all_friends:
            if all_friends[0].user == request.user:
                default_sender = all_friends[0].friends.user
            else:
                default_sender = all_friends[0].user
            form_sender_id = default_sender.id
            conversation = Message.objects.filter(Q(sender=user, receiver=default_sender)|Q(sender=default_sender, receiver=user)).order_by('created_at')

            #Count unread messages per sender
            for friend in all_friends:
                try:
                    # print friend.friends.user.get_full_name()
                    temp_num = Message.objects.filter(Q(sender=friend.friends.user, receiver=request.user, receiver_read=False)).count()
                except:
                    temp_num = 0

                # print "temp_num is "+str(temp_num)
                temp_num = int(temp_num)
                unread_messages.append(temp_num)

    except Exception as e:
        print e
        #if no friends found out.
        content = {
            'user':user,
            'form':form,
        }
        return render(request, 'vendroid/messages/online_message.html', content)



    #(2)show up conversation based on select friend from list######
    #or can be called by select friend
    if request.is_ajax() and "find_friend_message" in request.POST:
        print "find_friend_message happens"
        friend_user_id = request.POST.get('find_friend_message')
        # print friend_user_id
        if friend_user_id:
            friend_query = User.objects.filter(Q(id=friend_user_id))
            friends_tmp = AllFriends.objects.filter(Q(friends__user=friend_query))
            friends_send = None
            if friends_tmp:
                friends_send = friends_tmp[0].friends.user
                print friends_send.get_full_name

            conversation = Message.objects.filter(Q(sender=friend_query, receiver=user)|Q(sender=user, receiver=friend_query)).order_by('created_at')

            #receiver has read messages
            try:
                unread_messages = Message.objects.filter(Q(sender=friend_query, receiver=request.user, receiver_read=False))
                print unread_messages[0].message

                for message in unread_messages:
                    message.receiver_read = True
                    message.save()
            except:
                pass


            #by only rendering conversation.html page here,
            # it will be replaced according to different friends
            template = loader.get_template('vendroid/messages/conversation.html')

            content = {
                 'user': user,
                 'conversation': conversation,
            }
            data = RequestContext(request, content)
            return HttpResponse(template.render(data))

            # response = serializers.serialize("json", content)
            # print response

            #return HttpResponse(response, content_type="application/json")
            #return render(request, "vendroid/messages/conversation.html", content)
            #return render(request, serialize(content))

    #individually given chat friend name and images for avoiding scrollbar issue
    elif request.is_ajax() and "get_friend_name" in request.POST:
        # print "find_friend happens"
        friend_user_id = request.POST.get('get_friend_name')
        # print friend_user_id
        if friend_user_id:
            friend_query = User.objects.get(Q(id=friend_user_id))
            # print friend_query.get_full_name

            template = loader.get_template('vendroid/messages/partial/chat_friend.html')

            content = {
                'friend': friend_query,
            }
            data = RequestContext(request, content)
            return HttpResponse(template.render(data))

    #(2)search
    elif request.is_ajax() and "friend_name_search" in request.POST:
        # print "search happens"
        name = request.POST.get('friend_name_search')
        # print "name "+name
        split_result = name.split()
        #search for username, first name, last name, first_name&last_name
        first_name = split_result[0]
        if len(split_result) >= 2:
            last_name = split_result[1]
        else:
            last_name = ""
        # print "first_name "+first_name
        # print "last_name "+last_name
        friends, created = Friends.objects.get_or_create(user=request.user)
        friend_ids = friends.friends.all().values_list('id', flat=True)

        if not friend_ids:
            raise Http404

        userprofiles = UserProfile.objects.filter(Q(user__username__icontains=name)|Q(user__email__icontains=name)|Q(user__first_name__icontains=name)|Q(user__last_name__icontains=name)|Q(user__first_name__icontains=first_name, user__last_name__icontains=last_name)).filter(user__id__in=friend_ids).select_related('user').order_by('-subscribed')

        template = loader.get_template('vendroid/messages/select_result.html')

        content = {
            'userprofiles': userprofiles,
        }
        data = RequestContext(request, content)
        return HttpResponse(template.render(data))

        # response = serializers.serialize("json", userprofiles)
        # print response

        # return HttpResponse(response, content_type="application/json")
        # return render(request, 'vendroid/messages/select_result.html', content)


    #(4)Send the Message
    elif request.is_ajax() and "id_message" in request.POST:
        message = request.POST.get('id_message')
        send_id = request.POST.get('friend_id')
        send_id = int(send_id)
        #user the default id
        if send_id == 0:
            send_id = form_sender_id

        # image = request.POST.get('id_image')
        # # print message
        # if image:
        #     Message.objects.create(sender=user, receiver_id=form_sender_id, message=message, image=image)
        # else:
        #     Message.objects.create(sender=user, receiver_id=form_sender_id, message=message)
        is_friend = AllFriends.objects.filter(Q(user_id=send_id,friends__user=user)|Q(user=user, friends__user_id=send_id)).filter(Q(status=AllFriends.FOLLWOING)|Q(status=AllFriends.ACCEPTED)).count()
        # if not is_friend > 0:
            # template = loader.get_template('vendroid/messages/conversation.html')
            # message = "This user is not your friend."
            # content = {
            #      'message': message,
            # }
            # data = RequestContext(request, content)
            # return HttpResponse(template.render(data))
            # deduct = True
        if profile.type == UserProfile.PROFESSIONAL:
            if profile.amount > 0:
                # if deduct == True:
                profile.amount -= 1
                profile.save()
                Message.objects.create(sender=user, receiver_id=send_id, message=message)

                #get all conversation
                friend_query = User.objects.filter(Q(id=send_id))
                conversation = Message.objects.filter(Q(sender=friend_query, receiver=user)|Q(sender=user, receiver=friend_query)).order_by('created_at')

                template = loader.get_template('vendroid/messages/conversation.html')

                content = {
                     'user': user,
                     'conversation': conversation,
                     'messageSuccess': "You message has been sent successfully, remaining credit is: %d"%(profile.amount),
                }
                data = RequestContext(request, content)
                return HttpResponse(template.render(data))
            else:
                template = loader.get_template('vendroid/messages/conversation.html')
                message = "You donot have sufficient credit to send messages."
                content = {
                     'message': message,
                }
                data = RequestContext(request, content)
                return HttpResponse(template.render(data))
        else:
            Message.objects.create(sender=user, receiver_id=send_id, message=message)

            #get all conversation
            friend_query = User.objects.filter(Q(id=send_id))
            conversation = Message.objects.filter(Q(sender=friend_query, receiver=user)|Q(sender=user, receiver=friend_query)).order_by('created_at')

            template = loader.get_template('vendroid/messages/conversation.html')

            content = {
                 'user': user,
                 'conversation': conversation,
                 # 'messageSuccess': "You message has been sent, remaining credit is: %d"%(profile.amount),
            }
            data = RequestContext(request, content)
            return HttpResponse(template.render(data))
            # response = {}
            # response['message'] = message
            # # print response
            #
            # return HttpResponse(json.dumps(response), content_type="application/json")

            # response = serializers.serialize("json", conversation)
            # return HttpResponse(request, serialize(response))
    friend_id = None
    message_open = None
    if 'message_open' in request.GET and 'friend_id' in request.GET:
        message_open = request.GET.get('message_open')
        friend_id = request.GET.get('friend_id')
        print message_open, friend_id

    threads_list = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).values_list('sender', 'receiver')

    threads = set()
    for t in threads_list:
        if t[0] != request.user.id:
            threads.add(t[0])
        if t[1] != request.user.id:
            threads.add(t[1])

    threads = list(threads)
    all_threads = User.objects.filter(id__in=threads)

    content = {
        # 'user':user,
        'form':form,
        # 'conversation':conversation,
        # 'all_friends': all_friends,
        'all_threads': all_threads,
        'unknown_messages':unknown_messages,
        'friend': all_threads[0] if all_threads else None,
        # 'unread_messages':unread_messages,
        # 'message_open':message_open,
        # 'friend_id':friend_id,
        'unread_messages_unknown':unread_messages_unknown,
        'source': request.GET.get('source', ''),
        'video_call_init': request.GET.get('video_call_init', ''),
        # 'followings':followings,
    }

    template_name = 'vendroid/messages/online_message.html'

    return render(request, template_name, content)

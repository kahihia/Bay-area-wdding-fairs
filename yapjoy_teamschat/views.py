from django.shortcuts import render, HttpResponse
from datetime import datetime
from pusher import Pusher
# app_id = "297610"
# key = "ad53ba68297c735fc8fc"
# secret = "540e4161d210b3d9321a"
from restless.models import serialize
from django.views.decorators.csrf import csrf_exempt
from restless.http import Http201, Http404, Http400, HttpError, Http200
pusher = Pusher(app_id=u'297610', key=u'ad53ba68297c735fc8fc', secret=u'540e4161d210b3d9321a')
@csrf_exempt
def authView(request):
    if request.method == "POST":
        print 'request was post'
        print 'inside pusher view'
        socket_id = request.POST.get('socket_id')
        channel_name = request.POST.get('channel_name')
        print socket_id, channel_name
        # auth = pusher.authenticate(
        #
        #     channel=u'%s'%(channel_name),
        #
        #     socket_id=u'%s'%(socket_id)
        # )
        # print auth
        auth = pusher.authenticate(

            channel=u'%s' % (channel_name),
            #
            socket_id=u'%s'%(socket_id),

            custom_data={
                u'user_id': u'1',
                u'user_info': {
                    u'name': 'Administrator',
                    u'email': 'adeelpkpk@gmail.com'
                }
            }
        )
        # pusher.trigger([u'a_channel', u'another_channel'], u'an_event', {u'some': u'data'}, "1234.12")
        # pusher.trigger(u'%s'%(channel_name), u'test-event', {u'message': u'hello world'})
        # return `auth` as a response
        print auth
        return Http200(serialize(auth))
    print 'request was get'
    return HttpResponse('None')

from yapjoy_registration.models import UserProfile
import json
@csrf_exempt
def eventmanager(request):
    user = request.user
    if request.method == "POST":
        if "create_event" in request.POST:
            events = EventTeam.objects.filter(Q(user=user)|Q(friends__in=[user.id])).distinct('id')
            return render(request, 'vendroid/demov2/_eventmanager/_create_event.html',{
                'events':events
            })
        if "setup_event" in request.POST:
            # events = EventTeam.objects.filter(Q(user=user) | Q(friends__in=[user.id])).distinct('id')
            return render(request, 'vendroid/demov2/_eventmanager/_setup_event.html', {
                # 'event': event
            })
        elif "change_event" in request.POST:
            change_event = request.POST.get('change_event')
            event = None
            if change_event:
                event = EventTeam.objects.get(id=change_event)
            return render(request, 'vendroid/demov2/_eventmanager/_change_event.html', {
                'event': event
            })
        elif "add_channel" in request.POST:
            event_id = request.POST.get('event_id')
            return render(request, "vendroid/demov2/_eventmanager/_create_channel.html",{
                'event_id':event_id
            })
        elif "invite_user" in request.POST:
            invite_user = request.POST.get('invite_user')
            event_obj = None
            if invite_user:
                event_obj = EventTeam.objects.get(id=invite_user)
            return render(request, "vendroid/demov2/_eventmanager/_invite_bg_vendor.html",{
                'event':event_obj
            })
        elif "get_channels" in request.POST:
            get_channels = request.POST.get('get_channels')
            channels = ChannelChatList.objects.filter(team_id=get_channels)
            event_team = EventTeam.objects.filter(id=get_channels)

            creator = False
            if event_team:
                if event_team[0].user_id == user.id:
                    creator = True
            return render(request, "vendroid/demov2/_eventmanager/_view_channels.html",{
                'channels':channels,
                'user':user,
                'creator':creator,
                'event_id':get_channels,
            })
        elif "direct_message" in request.POST:
            direct_message = request.POST.get('direct_message')
            event = EventTeam.objects.get(id=direct_message)
            vendors = []
            bg = []
            if not request.user == event.user:
                bg.append(event.user)
            for o in event.friends.all():
                if o.userprofile.type == UserProfile.PROFESSIONAL:
                    vendors.append(o)
                else:
                    bg.append(o)
            final_list = {
                'bg': bg,
                'vendors': vendors
            }
            return render(request, "vendroid/demov2/_eventmanager/_add_friend.html",{
                'final_list':final_list,
                'event':event,
            })
        elif "get_team" in request.POST:
            get_team = request.POST.get('get_team')
            event = EventTeam.objects.get(id=get_team)
            vendors = []
            bg = []
            for o in event.friends.all():
                if o.userprofile.type == UserProfile.PROFESSIONAL:
                    vendors.append(o)
                else:
                    bg.append(o)
            final_list = {
                'bg':bg,
                'vendors':vendors
            }
            return render(request, 'vendroid/demov2/_eventmanager/_event_team.html',{
                'final_list':final_list,
            })


    return HttpResponse('Done')

def chatroom(request):
    # pusher.trigger(u'%s' % ('presence-channel'), u'new-comment',
    #                {u'message': u'this works great', 'user': 'administrator'})
    return render(request,'pusher/chat.html')
from django.db.models import Q
from .models import *
def chat_list(request, id):
    #event = EventTeam.objects.get_or_create(user=request.user)[0]
    user = request.user
    friends = FriendsChatList.objects.filter(Q(Q(user=user)|Q(friend=user)), team_id=id).distinct('id')
    friend_list = []
    if friends:
        for friend in friends:
            name = ""
            image = ""
            if user == friend.friend:
                name = friend.user.get_full_name()
                image = friend.user.userprofile.get_image_url()
            elif user == friend.user:
                name = friend.friend.get_full_name()
                image = friend.friend.userprofile.get_image_url()
            friend_list.append({
                'name':name,
                'channel':friend.channel_id,
                'event':friend.event,
                'image':image,
            })
    channels = ChannelChatList.objects.select_related('user').filter(Q(Q(friend__in=[user.id])|Q(user_id=user.id))&Q(team_id=id)).distinct('id')
    channel_list = []
    if channels:
        for channel in channels:
            channel_list.append({
                'name':channel.name,
                'channel':channel.channel_id,
                'event':channel.event,
            })
    friends_list = {
        'channels':channel_list,
        'friends':friend_list,
    }
    print serialize(friends_list)
    return Http200(serialize(friends_list))


from rest_framework import serializers




from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.contrib.auth import get_user_model # If used custom user model

from .serializer import MessageSerializer

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class send_message(CreateAPIView):

    model = FriendsChatList
    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,TokenAuthentication,SessionAuthentication,)
    serializer_class = MessageSerializer



@csrf_exempt
def send_message_ios(request):
    user = User.objects.get(id=1)

    channel = request.POST.get('channel_id')
    event = request.POST.get('event')
    message = request.POST.get('message')
    print channel, event, message, user
    sending_dict = {u'message': u'%s'%(message), 'user': user.get_full_name(), 'id':user.id}
    pusher.trigger(u'%s' % (channel), u'%s'%(event), sending_dict)
    return Http200(serialize(sending_dict))
from yapjoy_teamschat import serializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from yapjoy_teamschat.serializer import *


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class EventSerializerView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    serializer_class = serializer.EventSerializer
    serializer = serializer.EventSerializer
    model = serializer_class.Meta.model

    def get(self,request,format=None):
        feeds = self.model.objects.filter(Q(user=self.request.user)|Q(friends__in=[self.request.user.id])).distinct('id').select_related('user')#.order_by('created_at')
        serialized = self.serializer(feeds,many=True)
        return JSONResponse(serialized.data)


class EventCreate(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication,TokenAuthentication,SessionAuthentication)
    serializer_class = serializer.EventCreateSerializer

    def post(self, request, format=None):
        print ('post')
        serializer = self.serializer_class(data=request.data,  context={'user': request.user})
        if serializer.is_valid():
            print ("valid")
            serial = serializer.save()
            user = request.user
            print ("serial: ", serial['name'], str(serial['event_date']))
            event = EventTeam.objects.filter(user=user, name=serial['name'])
            data = {}
            for e in event:
                data = {
                    'event_id': e.id,
                    'name': e.name,
                    'event_date': e.event_date,
                    'event_user': e.user_id
                }

            return Response(data, status=status.HTTP_201_CREATED)

        else:
            print("Searializer is not valid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDelete(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.EventSerializerList
    authentication_classes = (CsrfExemptSessionAuthentication,TokenAuthentication,SessionAuthentication)
    def delete(self, request, pk ,format=None):
        print ("delete")
        snippet = EventTeam.objects.get(pk=pk)
        snippet.delete()
        return Response(status=status.HTTP_200_OK)


class EventList(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.EventSerializerList

    def get(self, request, format=None):
        print ("GET")
        event = EventTeam.objects.filter(user=request.user)
        serializer = self.serializer_class(event, many=True)
        return Response(serializer.data)


class EventEdit(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.EventEditSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication, SessionAuthentication)
    def get_object(self, pk):
        try:
            return EventTeam.objects.get(pk=pk)
        except EventTeam.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        print('get')
        event = self.get_object(pk)
        event = EventCreateSerializer(event)
        return Response(event.data)

    def put(self, request, pk, format=None):
        print('put')
        event = self.get_object(pk)
        print event
        print request.data
        serializer = EventCreateSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChannelCreateViewAPI(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.CreateChannelSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication, SessionAuthentication)
    """List All channels"""

    def get_object(self, pk):
        try:
            return ChannelChatList.objects.get(pk=pk)
        except EventTeam.DoesNotExist:
            raise Http404

    def get(self, request, event, format=None):
        print ("get")
        event_team = EventTeam.objects.filter(pk=event)
        print ("event: ", event_team)
        if event_team:
            channels = ChannelChatList.objects.filter(team=event_team)
            serializer = CreateChannelSerializer(channels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, event, format=None):
        serializer = self.serializer_class(data=request.data, context={'event':event})

        if serializer.is_valid():
            print ("valid")
            serializer.save()
            event = ChannelChatList.objects.filter(team_id=event, name=serializer['name'])
            data = {}
            for e in event:
                data = {
                    'channel': e.id,
                    'name': e.name,
                    'event_id': e.team_id,
                }

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        channel = self.get_object(pk)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendsCreateView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication,CsrfExemptSessionAuthentication)

    # permission_classes = (IsAuthenticated,)

    def get(self, request, team_id, user_friend_id, format=None):
        if team_id and user_friend_id:
            user = request.user
            print 'user: ',user
            friends = FriendsChatList.objects.filter(Q(Q(user_id=user_friend_id, friend_id=user.id)|Q(friend_id=user_friend_id, user_id=user.id))&Q(team_id=team_id))
            if not friends:
                print 'adding: ',user.id, user_friend_id, team_id
                friends = FriendsChatList.objects.create(user_id=user.id, friend_id=user_friend_id, team_id=team_id)
            # else:
            return Http200(serialize(friends))
            #     return HttpResponse("Friend already exist")


class ChannelCreateView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication,CsrfExemptSessionAuthentication)

    # permission_classes = (IsAuthenticated,)

    def get(self, request, channel_id, user_friend_id, format=None):
        if channel_id and user_friend_id:
            user = request.user
            print 'user: ',user
            channel = ChannelChatList.objects.filter(id=channel_id)
            if channel:
                channel = channel[0]
                user_get = User.objects.get(id=user_friend_id)
                channel.friend.add(user_get)
                channel.save()

            # else:
            return Http200(serialize(channel))
            #     return HttpResponse("Friend already exist")


class ChannelList(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.ChannelSerializer

    def get(self, request, id, format=None):
        print ("GET", id)
        event = ChannelChatList.objects.filter(team_id=id)
        serializer = self.serializer_class(event, many=True)
        return Response(serializer.data)


class ChannelDelete(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.ChannelSerializer

    # def post(self, request,pk ,format=None):
    #     print ('post')
    #     serializer = self.serializer_class(data=request.data, context={'user': request.user})
    #     if serializer.is_valid():
    #         print ("valid")
    #         serial = serializer.save()
    #         user = request.user
    #         print ("serial: ", serial['event_name'])
    #         event = Event.objects.get(id=id)
    #         if event:
    #
    #             event.delete()
    #
    #             data = {
    #                 ''
    #             }
    #
    #         return Response( status=status.HTTP_201_CREATED)
    #
    #     else:
    #         print("Searializer is not valid")
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, format=None):
        print ("GET", id)
        snippet = ChannelChatList.objects.filter(id=id, user=request.user)
        data = {}
        if snippet:
            for s in snippet:
                data = {
                    'channel_id': s.id,
                    'event_id': s.team_id
                }
            return Response(data,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, id, format=None):
        print ("delete")
        snippet = ChannelChatList.objects.get(id=id, user=request.user)
        snippet.delete()
        return Response(status=status.HTTP_200_OK)


class ChannelEdit(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializer.CreateChannelSerializer

    def get_object(self, id):
        try:
            return ChannelChatList.objects.get(id=id)
        except ChannelChatList.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        print('get')
        event = self.get_object(id)
        event = CreateChannelSerializer(event)
        return Response(event.data)

    def put(self, request, id, format=None):
        print('put')
        user = self.get_object(id)
        serializer = CreateChannelSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class messageHistory(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, code, format=None):
        print('get')

        messages = Messages.objects.select_related('sender').filter(Q(friends_chat_list__channel_id=code)|Q(channel_chat_list__channel_id=code)).order_by('created_at')
        response_send = []
        for message in messages:
            response_send.append({
                'picture':message.sender.get_image_url(),
                'name':message.sender.user.get_full_name(),
                'message':message.message,

            })
        return Http200(serialize(response_send))

"""
add by Chong
"""
class FriendList(APIView):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    #id is the event_id
    def get(self, request, id, format=None):
        user = request.user
        friends = FriendsChatList.objects.filter(Q(user=user)|Q(friend=user), team_id=id).distinct('id')
        friend_list = []
        if friends:
            for friend in friends:
                name = ""
                image = ""
                type = ""
                friend_id = 0
                if user == friend.friend:
                    friend_id = friend.user.id
                    name = friend.user.get_full_name()
                    image = friend.user.userprofile.get_image_url()
                    type = friend.user.userprofile.type
                elif user == friend.user:
                    friend_id = friend.friend.id
                    name = friend.friend.get_full_name()
                    image = friend.friend.userprofile.get_image_url()
                    type = friend.friend.userprofile.type
                friend_list.append({
                    "friend_id": friend_id,
                    'name':name,
                    'type': type,
                    'image': image,
                    'pusher_channel_id': friend.channel_id,
                    'pusher_event_name':friend.event,
                })

        return Http200(serialize(friend_list))

class ChannelList(APIView):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        user = request.user
        event = EventTeam.objects.get(id=id)
        channels = ChannelChatList.objects.select_related('user').filter(Q(Q(team__friends__in=[user.id])|Q(user_id=user.id))&Q(team=event)).distinct('id')
        channel_list = []
        if channels:
            for channel in channels:
                channel_list.append({
                    'id': channel.pk,
                    'name': channel.name,
                    'pusher_channel_id': channel.channel_id,
                    'pusher_event_name': channel.event,
                })

        return Http200(serialize(channel_list))

class ChannelFriendsList(APIView):
    authentication_classes = (TokenAuthentication,)
    #id is the channel_id
    def get(self, request, id, format=None):
        user = request.user
        try:
            channel = ChannelChatList.objects.get(Q(user=user), pk=id)
            print channel.name
            friend_list = []
            if channel:
                friends_id = channel.friend.values_list(flat=True)

                for f_id in friends_id:
                    friend = User.objects.get(pk=f_id)
                    friend_id = friend.id
                    name = friend.get_full_name()
                    image = friend.userprofile.get_image_url()
                    type = friend.userprofile.type

                    friend_list.append({
                        'name':name,
                        "friend_id": friend_id,
                        'channel_id': id,
                        'type': type,
                        'image':image,
                    })

            return Http200(serialize(friend_list))

        except Exception as e:
            print e
            raise Http404

class loginIOS(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        user = request.user
        sending = {
            "id":user.id
        }
        return Http200(serialize(sending))
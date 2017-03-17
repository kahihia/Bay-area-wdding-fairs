from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from yapjoy_registration.models import *
from django.db.models import Q
import requests
import json
import time
from django.core import serializers
from jqchat.models import *
@login_required(login_url='/login/')
@csrf_exempt
def video(request):
    # data_send = {
    #                         'content-type': 'application/json',
    #                          # "clientId" : "94a039cdf7cf9f213c97e671657165",
    #                          "Authorization" : "Apikey 94a039cdf7cf9f213c97e6716571656a1566dd53ca131849f07c2ce6b606",
    #                         # "clientSecret" : "6a1566dd53ca131849f07c2ce6b606",
    #                         # "uid" : "",
    #                         # "domain" : "https://www.yapjoy.com",
    #                         # "profile" : request.user.id,
    #
    #                          }
    # post_data = {
    #     "uid" : request.user.id,
    #     "domain" : "https://www.yapjoy.com/",
    #     "profile" : "standard",
    # }
    # # import certifi
    # print "before r"
    # r = requests.post("https://api.rtccloud.net/v2.0/provider/usertoken", headers=data_send, data=post_data)
    # print r
    # print "text", r.text
    # res = json.loads(r.text)
    # print res
    # response = None
    # # if res['result'] == "success":
    # #     print response
    # data = res['data']
    from opentok import OpenTok
    from opentok import MediaModes
    from opentok import Roles
    user = request.user
    session_id = None
    token = None
    if "token" in request.GET and "session_id" in request.GET:
        token = request.GET['token']
        session_id = request.GET['session_id']
        print "joining session: ",session_id
        print "joining token: ",token
    if 'create_session' in request.POST and request.is_ajax():

        print "creating a session"
        print request.POST.get('send_friend_id')

        opentok = OpenTok("45497542", "a4556f3ad769a0b28324b52e9788423d38fc27f0")

        session = opentok.create_session()
        session = opentok.create_session(media_mode=MediaModes.routed)
        session_id = session.session_id

        token = opentok.generate_token(session_id)
        # Generate a Token by calling the method on the Session (returned from create_session)
        token = session.generate_token()


        # Set some options in a token
        token = session.generate_token(role=Roles.moderator,
                                       expire_time=int(time.time()) + 60,
                                       data=u'name=%s'%(user.get_full_name()))
        print "token: ",token
        message_rep = None
        link = '/video/?token=%s&session_id=%s'%(token, session_id)
        try:
            id = request.POST.get('send_friend_id')
            print 'id is: ',id
            user = User.objects.get(id=id)
            print user.email
            message_rep = "%s you have recieved a video call from %s<br /><br /><a data-url='%s' href='#' style='pointer: cursor;' class='accept-call btn vd_btn'><i class='fa fa-video-camera append-icon'></i>Accept Call</a>"%(user.get_full_name(), request.user.get_full_name(), link)
            Message.objects.create(sender=request.user, receiver_id=id, subject="Video call request", message=message_rep)
            Message.objects.create(sender=user, receiver_id=request.user.id, subject="Video call request", message=message_rep)
        except Exception as e:
            print "exc call: ", e
        return HttpResponse(json.dumps({
            'link':link,
            'message':message_rep,
        }))
        # example https://127.0.0.1:8008/video/?session_id=2_MX40NTQ5NzU0Mn5-MTQ1NTkzNjE5MTc3M35va3VBbzRQV2t4RXU3aWNLOHNXeEFCZW1-fg&token=T1==cGFydG5lcl9pZD00NTQ5NzU0MiZzaWc9YzIwYTA0N2RmNTIyOWQ4Mzc0MjdkMzgyNTVjZWMxMTBhNWI3ZGI2MTpub25jZT0yODIwMzMmY29ubmVjdGlvbl9kYXRhPW5hbWUlM0RkYXRhYmFzZStuYW1lK0toYW4mY3JlYXRlX3RpbWU9MTQ1NTkzNjE5MSZyb2xlPW1vZGVyYXRvciZleHBpcmVfdGltZT0xNDU1OTM2MjUxJnNlc3Npb25faWQ9Ml9NWDQwTlRRNU56VTBNbjUtTVRRMU5Ua3pOakU1TVRjM00zNXZhM1ZCYnpSUVYydDRSWFUzYVdOTE9ITlhlRUZDWlcxLWZn
        # return HttpResponseRedirect('?session_id=%s&token=%s'%(session_id, token))
    ThisRoom = get_object_or_404(Room, id=1)
    all_friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(type=AllFriends.PROFESSIONAL)&~Q(status=AllFriends.INVITED)).select_related('user','user__userprofile')
    return render(request, 'vendroid/video/video.html',{
        'all_friends':all_friends,
        'session_id':session_id,
        'token':token,
        'user':user,
        'room':ThisRoom,
        # 'data':data,
    })

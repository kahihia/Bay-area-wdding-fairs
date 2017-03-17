import json

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.conf import settings
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.decorators import api_view
from opentok import OpenTok, MediaModes

from yapjoy_registration.models import UserProfile
from .models import ChatConnection, ChatConnection, NotificationConnection, Message
from .serializers import UserSerializer, MessageSerializer


TOKBOX_KEY = settings.TOKBOX_KEY
TOKBOX_SECRET = settings.TOKBOX_SECRET


@login_required
def video_chat(request):

    return render(request, 'yapjoy_messages/video_chat.html', {
        'user2': User.objects.get(id=request.GET.get('user'))
    })


@login_required
def get_vchat_session(request):
    opentok = OpenTok(TOKBOX_KEY, TOKBOX_SECRET)

    user2 = User.objects.get(id=request.GET.get('user'))
    connection = ChatConnection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)).filter(
        Q(sender=user2) | Q(receiver=user2)
    ).filter(chat_type=ChatConnection.VIDEO)

    if not connection:
        session = opentok.create_session()
        ChatConnection.objects.create(
            sender=request.user,
            receiver=user2,
            session_id=session.session_id,
            chat_type=ChatConnection.VIDEO,
        )
        connection = ChatConnection.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)).filter(
            Q(sender=user2) | Q(receiver=user2)
        ).filter(chat_type=ChatConnection.VIDEO)

    token = opentok.generate_token(connection[0].session_id)

    session_dict = {
        'apiKey': TOKBOX_KEY,
        'sessionId': connection[0].session_id,
        'token': token,
    }
    return HttpResponse(json.dumps(session_dict, ensure_ascii=False))


@login_required
def text_chat(request):

    return render(request, 'yapjoy_messages/text_chat.html', {
        'user2': User.objects.get(id=request.GET.get('user'))
    })


@login_required
def get_tchat_session(request):
    opentok = OpenTok(TOKBOX_KEY, TOKBOX_SECRET)

    user2 = User.objects.get(id=request.GET.get('user'))
    connection = ChatConnection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)).filter(
        Q(sender=user2) | Q(receiver=user2)
    ).filter(chat_type=ChatConnection.TEXT)

    if not connection:
        session = opentok.create_session(media_mode=MediaModes.routed)

        ChatConnection.objects.create(
            sender=request.user,
            receiver=user2,
            session_id=session.session_id,
            # archive_id=archive.id,
            chat_type=ChatConnection.TEXT,
        )
        connection = ChatConnection.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)).filter(
            Q(sender=user2) | Q(receiver=user2)
        ).filter(chat_type=ChatConnection.TEXT)

    token = opentok.generate_token(connection[0].session_id)
    # archive = opentok.get_archive(connection.archive_id)

    session_dict = {
        'apiKey': TOKBOX_KEY,
        'sessionId': connection[0].session_id,
        'token': token,
        # 'archive': archive,
    }
    return HttpResponse(json.dumps(session_dict, ensure_ascii=False))


@login_required
def get_tchat_archive(request):

    user2 = User.objects.get(id=request.GET.get('user'))
    Message.objects.filter(receiver=user2, sender=request.user).update(receiver_read=True)
    history = Message.objects.filter(
        Q(sender=request.user) & Q(receiver=user2) |
        Q(sender=user2) & Q(receiver=request.user)).order_by('-created_at')

    if not request.GET.get('all', False):
        history = history[:5]

    history = reversed(history)

    return HttpResponse(serializers.serialize('json', history))


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def put_tchat_data(request):

    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.type == UserProfile.PROFESSIONAL and user_profile.amount < 1:
        return HttpResponse(
            'Error: You do not have enough creadits to send a message')

    if request.POST.get('message') and request.POST.get('user'):
        user2 = User.objects.get(id=request.POST.get('user'))
        Message.objects.create(
            sender=request.user,
            receiver=user2,
            message=request.POST.get('message'),
        )

        if user_profile.type == UserProfile.PROFESSIONAL:
            user_profile.amount = user_profile.amount - 1
            user_profile.save()
            return HttpResponse(
                'Message sent. You have {} creadits remaining'.format(
                    user_profile.amount))

        return HttpResponse('')

    return HttpResponse(
        'Error: Please enter a message')


@login_required
def get_notification_session(request):

    user = User.objects.get(id=request.GET.get('user'))
    connection, created = NotificationConnection.objects.get_or_create(
                            user=user)
    opentok = OpenTok(TOKBOX_KEY, TOKBOX_SECRET)

    if not connection.session_id:
        session = opentok.create_session(media_mode=MediaModes.routed)
        connection.session_id = session.session_id
        connection.save()

        if not session:
            return HttpResponse(json.dumps({'error': 'Unable to generate session'}, ensure_ascii=False))

    token = opentok.generate_token(connection.session_id)

    session_dict = {
        'apiKey': TOKBOX_KEY,
        'sessionId': connection.session_id,
        'token': token,
    }
    return HttpResponse(json.dumps(session_dict, ensure_ascii=False))


@login_required
def get_message_count(request):

    messages = Message.objects.filter(receiver=request.user, receiver_read=False).value_list('sender')
    return HttpResponse(len(messages))


@login_required
def register_video_call(request):

    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.type == UserProfile.PROFESSIONAL:

        if user_profile.amount < 1:
            return HttpResponse(
                'Error: You do not have enough creadits to send a message')

        user_profile.amount = user_profile.amount - 1
        user_profile.save()
        return HttpResponse('You have {} creadits remaining'.format(
            user_profile.amount))

    return HttpResponse('')


@login_required
def update_last_seen(request):

    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.last_seen = timezone.now()
    user_profile.save()

    return HttpResponse('')


@login_required
def is_online(request):
    try:
        user_profile = UserProfile.objects.get(user__id=request.GET.get('user'))

        duration = (timezone.now() - user_profile.last_seen).total_seconds()
        response = {
            'duration': duration,
            'is_online': True if duration < 30 else False,
            'user': user_profile.user.username,
        }

        return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        return HttpResponse('', content_type='application/json')


@login_required
@api_view(['GET', 'HEAD'])
def get_chat_user_list(request):
    threads_list = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).values_list('sender',
                                                                                                         'receiver')

    threads = set()
    for t in threads_list:
        if t[0] != request.user.id:
            threads.add(t[0])
        if t[1] != request.user.id:
            threads.add(t[1])

    threads = list(threads)
    all_threads = User.objects.filter(id__in=threads)
    serializer = UserSerializer(all_threads, many=True)
    return Response(serializer.data)


@login_required
def get_user_picture_url(request):
    return HttpResponse('https://yapjoy-static.s3.amazonaws.com/media/media/tempPhoto.png')


@login_required
@api_view(['GET', 'HEAD'])
def get_messages(request):

    user2 = User.objects.get(id=request.GET.get('user'))
    Message.objects.filter(receiver=user2, sender=request.user).update(receiver_read=True)
    history = Message.objects.filter(
        Q(sender=request.user) & Q(receiver=user2) |
        Q(sender=user2) & Q(receiver=request.user)).order_by('-created_at')

    if not request.GET.get('all', False):
        history = history[:5]

    history = reversed(history)
    serializer = MessageSerializer(history, many=True)
    return Response(serializer.data)

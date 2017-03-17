from rest_framework import serializers
from .models import FriendsChatList, EventTeam, ChannelChatList, Messages
from rest_framework.authtoken.models import Token
from pusher import Pusher
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
pusher = Pusher(app_id=u'297610', key=u'ad53ba68297c735fc8fc', secret=u'540e4161d210b3d9321a')


class MessageSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(UserRegistrationSerializer, self).__init__(many=many, *args, **kwargs)
 #   access_token = serializers.ReadOnlyField()
    message = serializers.CharField(max_length=500)
    class Meta:
        model = FriendsChatList
        fields = ('id','event', 'channel_id','message')
        # write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        print validated_data
        user = self.context['request'].user

        channel = validated_data['channel_id']
        event = validated_data['event']
        message = validated_data['message']
        print channel, event, message, user
        friends_chat_list = None
        channel_chat_list = None
        team = None
        try:
            friends_chat_list = FriendsChatList.objects.get(channel_id=channel)
            team = friends_chat_list.team
        except:
            pass
        try:
            channel_chat_list = ChannelChatList.objects.get(channel_id=channel)
            team = channel_chat_list.team
        except:
            pass


        message_obj = Messages.objects.create(message=message,
                                          sender=user.userprofile,
                                          friends_chat_list=friends_chat_list,
                                          channel_chat_list=channel_chat_list,
                                          team=team,


                                          )
        sending_dict = {u'message': u'%s' % (message), 'user': user.get_full_name(), 'id': user.id, 'image':user.userprofile.get_image_url()}
        pusher.trigger(u'%s' % (channel), u'%s' % (event), sending_dict)
        print "sending back"
        return sending_dict

    # user = User.objects.create(
    #     username=validated_data['username'],
    #     email=validated_data['username'],
    #     # first_name=validated_data['first_name'],
    #     # last_name=validated_data['last_name']
    # )
    #
    # user.set_password(validated_data['password'])
    # user.save()
    # token = Token.objects.create(user=user)
    # context = {
    #     'username': user.username,
    #     'password': user.password,
    #     'first_name': user.first_name,
    #     'last_name': user.last_name,
    #     'access_token': token.key,
    # }
    # return context

from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    #profile_user = ProfileSerializer(source='profile', read_only=True)
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email',
                  # 'profile_user'
                  )



class EventSerializer(serializers.HyperlinkedModelSerializer):
    # post__user = UserSerializer(many=False, read_only=True)
    # user_data = UserSerializer(source='user', read_only=True)
    user = UserSerializer(read_only=True)
    friends = UserSerializer(read_only=True, many=True)
    # post__user = serializers.RelatedField(read_only=True)
    class Meta:
        model = EventTeam
        fields = ('user','friends','created_at','id','name'
                  # 'image',
                  )

    def create(self, validate_data):
        print ("create: ", validate_data)
        return validate_data

    def validate(self, attrs):
        print ("attrs: ", attrs)
        return attrs


class EventSerializerList(serializers.ModelSerializer):
    class Meta:
        model = EventTeam
        fields = ('name', 'user', 'event_date')


class EventCreateSerializer(serializers.ModelSerializer):

    event_date = serializers.DateField()

    class Meta:
        model = EventTeam
        fields = ('name', 'event_date',
        # 'image',
        )

    def create(self, validated_data):
        print ("create: ", validated_data)
        event = EventTeam.objects.create(user=self.context.get("user"), name=validated_data['name'], event_date=validated_data['event_date'])
        return validated_data

    def validate(self, attrs):
        print ("validate: ", attrs)
        try:
            if attrs['name'] != None and attrs['event_date'] != None:
                return attrs
        except ValidationError as e:

            msg = _('Enter Valid data.')
            raise serializers.ValidationError(
                msg
            )

        return attrs


class EventEditSerializer(serializers.ModelSerializer):

    event_date = serializers.DateField()

    class Meta:
        model = EventTeam
        fields = ('name', 'event_date',
        # 'image',
        )

    def create(self, validated_data):
        print ("create: ", validated_data)
        event = EventTeam.objects.get(id=self.context.get("id"))
        if event:
            event.name = validated_data['name']
            event.event_date = validated_data['event_date']
            event.save()
        return validated_data

    def validate(self, attrs):
        print ("validate: ", attrs)
        try:
            if attrs['name'] != None and attrs['event_date'] != None:
                return attrs
        except ValidationError as e:

            msg = _('Enter Valid data.')
            raise serializers.ValidationError(
                msg
            )

        return attrs


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelChatList
        fields = ['name']


class CreateChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelChatList
        fields = ['name']

    def create(self, validated_data):
        name = validated_data['name'],
        try:
            print ("u: ", self.context.get("user"))
            event = EventTeam.objects.get(id=self.context.get('event'))
            channel = ChannelChatList.objects.create(name=validated_data['name'], team=event, user=event.user )
            print ("channel: ", channel)
        except ValidationError as e:
            msg = _('Name is not valid')
            raise serializers.ValidationError(
                msg
            )

        return validated_data

    def validate(self, data):
        print("email: ",self.context.get("user"), self.context.get('event'))
        # try:
        #     event = EventTeam.objects.get(id=self.context.get('event'))
        #     channel = ChannelChatList.objects.create(name=data['name'], team=event, user=self.context.get("user"))
        #     print ("channel: ", channel)
        # except ValidationError as e:
        #     msg = _('Name is not valid')
        #     raise serializers.ValidationError(
        #         msg
        #     )
        if data['name'] == None or data['name'] == "":
            msg = ('Name is not valid')
            raise serializers.ValidationError(
                    msg
                )

        return data



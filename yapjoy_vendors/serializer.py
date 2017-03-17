from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import (
    EmailField,
    ModelSerializer,
    ValidationError
)
# Vendor Registration
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
import string
import random
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from yapjoy_registration.models import *


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class VendorSerializerRegister(serializers.ModelSerializer):
    # full_name = serializers.SerializerMethodField('get_full_name')
    # Name = serializers.SerializerMethodField(source='first_name')
    # password = serializers.CharField(write_only=True,required=True)
    full_name = serializers.CharField(max_length=100,
        style={'autofocus': True},write_only=True,required=True)
    # email = serializers.CharField(max_length=100,
    #     style={'placeholder': 'Email', 'autofocus': True}, write_only=True,required=True)
    # business_location = serializers.CharField(max_length=100,
    #     style={'placeholder': 'Business Location', 'autofocus': True},write_only=True,required=True)
    # phone = serializers.CharField(max_length=100,
    #     style={'placeholder': 'Phone', 'autofocus': True},write_only=True,required=True)
    # profession = serializers.CharField(max_length=100,
    #     style={'placeholder': 'Profession', 'autofocus': True},write_only=True,required=True)

    class Meta:
        model = VendorRegistration
        fields = (
            'full_name','email', 'phone', 'business_location', 'profession'
        )
        # exclude = ('first_name',)
        extra_kwargs = {'email': {'required': True}, }
        # for extra
    #             extra_kwargs = {"username": {"error_messages": {"required": "Give yourself a username"}}}
    def get_full_name(self, obj):
        print "function: ", obj
        return '{} {}'.format(obj.first_name, obj.last_name)

    def create(self, validated_data):
        register_user = {
            'email': validated_data['email'],
        }
        print('email: ',validated_data['email'])
        email = validated_data['email']
        business_location = validated_data['business_location']
        profession = validated_data['profession']

        name = validated_data['full_name'].split(' ')
        print "validate: ", email, profession, validated_data
        user = User.objects.create(username=email, email=email, first_name=name[0], last_name=name[1])
        verification_code = id_generator(size=6)
        VendorRegistration.objects.create(user=user,email=user.email,
                                          business_location=business_location,
                                          code=id_generator(),
                                          verification_code= verification_code,
                                          profession=profession)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.phone = validated_data['phone']
        user_profile.profession = validated_data['profession']
        user_profile.save()
        # user.set_password(validated_data['password'])

        send_email(email, 'Email Verification Code',
                   'Use the following email verification code:<br /><br /><h1>%s</h1><br /><br />If you have not initiated this, contact info@yapjoy.com or reply to this email with your concerns.' % (
                   verification_code), 'YapJoy Vendors Email Verification Code')

        # user = authenticate(username=validated_data['email'], password=validated_data['password'])

        return validated_data

    '''validate email'''
    def validate(self, data):

        try:
            validate_email(data['email'])
        except ValidationError as e:
            msg = _('Enter a valid email address.')
            raise serializers.ValidationError(
                msg
            )

        user_qs = User.objects.filter(email__iexact=data['email'])
        if user_qs.exists():
            msg = _('Email already exists.')
            raise serializers.ValidationError(
                msg
            )

        return data


class ConfirmSerializer(serializers.Serializer):
    verification_code = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = VendorRegistration
        fields = (
            'verification_code'
        )

    def create(self, validated_data):
        code = validated_data['verification_code'],

        print ("create: ",code )

        # user = VendorRegistration.objects.filter(verification_code=code)
        # if user != None:
        #     for u in user:
        #         u.verification_code = None
        #         u.save()

        return validated_data

    def validate(self, data):
        print("email: ",self.context.get("email"))
        try:
            user_qs = VendorRegistration.objects.filter(email__iexact=self.context.get("email"), verification_code=data['verification_code'])
            profile, created = UserProfile.objects.get_or_create(user__email=self.context.get('email'))
            if created:
                for us in user_qs:
                    print ("in loop")
                    profile.user = us.user
                    profile.profession = us.profession
                    profile.save()

            else:
                for us in user_qs:
                    print ("in loop")
                    profile.profession = us.profession
                    profile.save()

        except ValidationError as e:
            msg = _('Code is not valid')
            raise serializers.ValidationError(
                msg
            )

        if not user_qs:
            msg = _('Code is not valid')
            raise serializers.ValidationError(
                msg
            )

        return data


class SetPassword(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'password',
        ]
        extra_kwargs = {"password":
                            {"write_only": True}
                        }

    def create(self, validated_data):
        password = validated_data['password'],
        print ("password: ",password)
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'first_name', 'last_name', 'email',)
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = super(UserSerializer, self).restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        print ("username: ", username, password)

        if username and password:
            user = authenticate(username=username, password=password)
            print "user: ", user
            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs


def send_email(sendTo, message, title, subject):
    # data = {
    #     'amount' : '10000',
    #     'name' : 'JOHN SMITH',
    #     'address' : '100 MAIN ST PO BOX 1022 SEATTLE WA 98104 USA',
    # }
    context = {
                'message':message,
                'title':title,
                }
    html_content = render_to_string('email/generic_email.html', context=context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, 'info@yapjoy.com', [sendTo])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print ('Email sent')
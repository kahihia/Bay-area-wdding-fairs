from yapjoy_vendors.serializer import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, parsers, renderers
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.core.urlresolvers import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from yapjoy_registration.models import *
from django.contrib.auth import authenticate, login as auth_login


class VendorRegister(APIView):
    serializer_class = VendorSerializerRegister
    permission_classes = (AllowAny,)

    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'vendroid/demov2/vendors/profile/vendor_profileFormv2.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):

        # return render(request,'vendroid/demov2/vendors/profile/vendor_profileFormv2.html',{'serializer': self.serializer_class})
        return Response({'serializer':  self.serializer_class, 'style': self.style})

    def post(self, request,  format=None):

        data = request.data

        serializ = self.serializer_class(data=data)
        # print ("serializer: ", serializ)
        if serializ.is_valid():

            user = serializ.save()
            email = user['email']
            print "serail: ", user
            user = User.objects.get(email__iexact=email)
            token = Token.objects.get_or_create(user=user)[0]
            data = {
                'id': user.id,
                'email': user.email,
                'token': token.key
            }

            url = reverse('vendors__verification', kwargs={'token':token, 'email':user.email})
            return HttpResponseRedirect(url)
            """For the DRF API  only """
            # return Response(data, status=status.HTTP_201_CREATED)
        else:
            print("Searializer is not valid")

            return Response({'serializer': serializ, 'style': self.style})


class EmailVerification(APIView):
    serializer_class = ConfirmSerializer

    renderer_classes = (TemplateHTMLRenderer,)

    template_name = 'vendroid/demov2/vendors/profile/vendor_emailverificationFormv2.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        print ("args: ", args, kwargs)
        return Response({'serializer': self.serializer_class, 'email': kwargs['email'], 'style': self.style})

    def post(self, request, token, email, format=None):

        data = request.data
        serializ = self.serializer_class(data=data,  context={'email': email})

        if serializ.is_valid():
            serial = serializ.save()
            code = serial['verification_code']

            verification = VendorRegistration.objects.get(user__email=email)
            token = Token.objects.get(key=token, user=verification.user)
            # if verification:
            #     if verification.code == code:
            #         data = {
            #             'id': verification.user.id,
            #             'email': verification.email,
            #             'token': token.key
            #         }
            #         url = reverse('vendors__setpassword', kwargs={'token': token, 'email': verification.email})
            #         return HttpResponseRedirect(url)
            #     else:
            #         print ("no code ")
            #         return Response({'serializer': serializ, 'style': self.style})
            url = reverse('vendors__setpassword', kwargs={'token': token, 'email': verification.email})
            return HttpResponseRedirect(url)
                    # return Response(data, status=status.HTTP_201_CREATED)
            # else:
            #     print ("unauthorized")
            #     return Response({'serializer': serializ, 'style': self.style})
            #     # return Response(serializ.errors, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            print("Searializer is not valid")

            return Response({'serializer': serializ, 'style': self.style})

from django.contrib.auth import authenticate, login as auth_login

class SetPassword(APIView):
    serializer_class = SetPassword

    renderer_classes = (TemplateHTMLRenderer,)

    template_name = 'vendroid/demov2/vendors/profile/vendor_setPasswordFormv2.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        print ("args: ", args, kwargs)
        return Response({'serializer': self.serializer_class, 'email': kwargs['email'], 'style': self.style})

    def post(self, request, token, email, format=None):
        print ("requestEmail: ", request.data)
        serializ = self.serializer_class(data=request.data)

        if serializ.is_valid():
            serial = serializ.save()
            code = serial['password']
            print("code: ", code)
            user = User.objects.get(email=email)
            print "user: ", user, email
            token = Token.objects.get(user=user, key=token)
            if user:
                """password Store"""
                user.set_password(code)
                user.save()

                user_auth = authenticate(username=user.email, password=code)
                print "login: ", user_auth, user.username, user.password
                sub = None
                if user_auth.is_active:
                    user_auth.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth_login(request, user_auth)
                    print 'auth'
                    data = {
                        'id': user.id,
                        'email': user.email,
                        'token': token.key
                    }
                # return Response(data, status=status.HTTP_201_CREATED)
                # return Response({'serializer': serializ, 'style': self.style})
                    url = reverse('vendors__profile')
                    return HttpResponseRedirect(url)
            else:
                return Response({'serializer': serializ, 'style': self.style})
                # return Response(serializ.errors, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            print("Searializer is not valid")
        return Response({'serializer': serializ, 'style': self.style})


class LoginUser(APIView):
        throttle_classes = ()
        permission_classes = (AllowAny,)
        # parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
        # renderer_classes = (renderers.JSONRenderer,)
        serializer_class = AuthTokenSerializer

        def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            token, created = Token.objects.get_or_create(user=user)
            user_info = UserProfile.objects.get(user=user)
            return Response({'token': token.key , 'user_id': user_info.user.id, 'username': user_info.user.username, 'user_imageurl': str(user_info.image)})


class LogoutUser(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        # request.user.auth_token.delete()
        request.session.flush()
        return Response(status=status.HTTP_200_OK)


class VendorRegisterIOS(APIView):
    serializer_class = VendorSerializerRegister
    permission_classes = (AllowAny,)

    # renderer_classes = (TemplateHTMLRenderer,)
    # template_name = 'vendroid/demov2/vendors/profile/vendor_profileFormv2.html'
    # style = {'template_pack': 'rest_framework/vertical/'}
    #
    # def get(self, request, *args, **kwargs):
    #
    #     # return render(request,'vendroid/demov2/vendors/profile/vendor_profileFormv2.html',{'serializer': self.serializer_class})
    #     return Response({'serializer':  self.serializer_class, 'style': self.style})
    #     # return Response(self.template_name)
    def post(self, request,  format=None):

        data = request.data

        serializ = self.serializer_class(data=data)
        # print ("serializer: ", serializ)
        if serializ.is_valid():

            user = serializ.save()
            email = user['email']
            user = User.objects.get(email__iexact=email)
            token = Token.objects.get_or_create(user=user)[0]
            data = {
                'id': user.id,
                'email': user.email,
                'token': token.key
            }
            """"""
            # url =  reverse('vendors__verification', kwargs={'token':token, 'email':user.email})
            # return HttpResponseRedirect(url)
            """For the DRF API  only """
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            print("Searializer is not valid")
            # return render(request, 'vendroid/demov2/vendors/profile/vendor_profileFormv2.html',
            #               {'serializer': self.serializer_class, 'error':serializ.errors})

            # return Response({'serializer': serializ, 'style': self.style})
            return Response(serializ.errors, status=status.HTTP_400_BAD_REQUEST )


class EmailVerificationIOS(APIView):
    serializer_class = ConfirmSerializer

    # def get(self, request):
    #     print ("req: ", request.data, request)
    #
    #     return

    def post(self, request, token, email, format=None):
        print ("requestEmail: ", request.data)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serial = serializer.save()
            code = serial['verification_code']
            print("code: ", code)
            verification = VendorRegistration.objects.get(user__email=email)
            token = Token.objects.get(key=token, user=verification.user)
            if verification:

                data = {
                    'id': verification.user.id,
                    'email': verification.email,
                    'token': token.key
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            print("Searializer is not valid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordIOS(APIView):
    serializer_class = SetPassword

    def post(self, request, token, email, format=None):
        print ("requestEmail: ", request.data)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serial = serializer.save()
            code = serial['password']
            print("code: ", code)
            user = User.objects.filter(email=email)
            token = Token.objects.get(user=user, key=token)
            if user:
                for u in user:
                    u.set_password(code)
                    u.save()
                    authenticate(username=u.username, password=u.password)
                    print (u.username, u.password,authenticate(username=u.username, password=u.password))
                    data = {
                        'id': u.id,
                        'email': u.email,
                        'token': token.key
                    }
                    return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            print("Searializer is not valid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth.models import User
from django.shortcuts import redirect

def update_member_profile(backend, user, response, details, is_new=False, *args, **kwargs):
    try:
        print is_new
        print response
        # print "----"
        print details
        if is_new:
            print "here"
            print is_new
            print response['access_token']
            print details['username']
            print details['first_name']
            print details['email']
            user = None
            try:
                print "Inside Try"
                print "Email id: ", details['email']
                user = User.objects.get(email=details['email'])
                user.username = details['email']
                user.first_name = details['first_name']
                user.last_name = details['last_name']
                user.save()

                print "End Try"
            except User.DoesNotExist as e:
                print e

            # return redirect('/register_confirm/')
            # print "here"
            # print response['access_token']
            # print '/register-by-token/facebook/%s'%(response['access_token'])
            #
            # return redirect('/register-by-token/facebook/?access_token='+response['access_token']+'')
        else:
            print is_new
            user = None
            try:
                print "Inside Try"
                print "Email else: ", details['email']
                user = User.objects.get(email=details['email'])

                user.first_name = details['first_name']
                user.last_name = details['last_name']
                user.save()

                print "End Try"
            except User.DoesNotExist as e:
                print e

    except Exception as e:
        print e
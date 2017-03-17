# Create your views here.

from django.shortcuts import redirect, render_to_response, render
from django.conf import settings
from django.core.urlresolvers import reverse
from contact_importer.providers.google import GoogleContactImporter
from live_custom_provider import CustomLiveContactImporter
from yahoo_custom_provider import CustomYahooContactImporter
from django.contrib.auth.models import User
# from pac.util import send_invite_email
from django.http import HttpResponseRedirect
# from pac.models import Relationship

providers = {
    "google": GoogleContactImporter,
    "live": CustomLiveContactImporter,
    "yahoo": CustomYahooContactImporter
}
def success(request):
    msg = "You have successfully invited your friends to YapJoy."
    return render(request,"vendroid/contacts/success.html",
                  {'msg': msg}
    )
def index(request):
    provider = request.GET.get('provider')
    if provider:
        provider_instance = _get_provider_instance(provider, _get_redirect_url(request))
        if provider == "yahoo":
            provider_instance.get_request_token()
            request.session["oauth_token_secret"] = provider_instance.oauth_token_secret
        return redirect(provider_instance.request_authorization())
    return render_to_response("contacts/index.html")
from yapjoy_registration.models import AllFriends, Friends
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
def invite(request):
    if request.method == 'POST' and 'email' in request.POST:
        print request.POST
        invite_ables = request.POST.getlist('email', None)
        if invite_ables:
            friends = Friends.objects.get(user=request.user)
            for email in invite_ables:
                print "Sending email to: ",email.strip()
                user_new = None
               # if re.match(r"^[a-zA-Z0-9._]+\@[a-zA-Z0-9._]+\.[a-zA-Z]{3,}$", email.strip()):
                try:
                    print "invited_%s"%(email.strip())
                    user_new = User.objects.create(username="invited_%s"%(email.strip()), email="invited_%s"%(email.strip()))
                    AllFriends.objects.create(friends=friends, user=user_new, status=AllFriends.INVITED)
                except Exception as e:
                    print e
                    return HttpResponseRedirect('')
                context = {
                    'link':"https://www.yapjoy.com/invitation/accept/%s"%(user_new.email)
                }
                html_content = render_to_string('email/invite.html', context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives('YapJoy Invitation by %s'%(request.user.get_full_name()), text_content, 'info@yapjoy.com', [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            #send_invite_email(invite_ables)
            return HttpResponseRedirect('/invites/success')
    provider = request.GET.get('provider')

    if not provider:
        return redirect(reverse("contacts_index"))

    code = request.GET.get('code')
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    redirect_url = _get_redirect_url(request)
    provider_instance = _get_provider_instance(provider, redirect_url)
    users_list = []
    invite_ables = []
    contacts = None
    if provider == "yahoo":
        print oauth_token
        provider_instance.oauth_token = oauth_token
        provider_instance.oauth_verifier = oauth_verifier
        provider_instance.oauth_token_secret = request.session["oauth_token_secret"]
        provider_instance.get_token()
        contacts = provider_instance.import_contacts()
        del request.session["oauth_token_secret"]
    else:
        access_token = provider_instance.request_access_token(code)
        contacts = provider_instance.import_contacts(access_token)
        print contacts
        print access_token
    for c in contacts:
        try:
            usr = User.objects.get(username=c)
            # try:
            #     relation = Relationship.objects.get(from_users=request.user, to_users=usr)
            #     usr.relation_status = relation.relation_status
            # except Relationship.DoesNotExist:
            #     try:
            #         relation = Relationship.objects.get(to_users=request.user, from_users=usr)
            #         usr.relation_status = "FOLLOWER"
            #     except:
            #         pass
            # except:
            #     pass
            users_list.append(usr)
        except User.DoesNotExist:
            invite_ables.append(c)

    return render(request,"vendroid/contacts/invite.html", {"contacts": contacts, "users_list":users_list,'invite_ables':invite_ables})

def _get_redirect_url(request):
        provider = request.GET.get('provider')
        invite_url = "%s?provider=%s" % (reverse("invite_contacts"), provider)
        request_scheme = "https" if request.is_secure() else "http"
        redirect_url = "%s://%s%s" % (request_scheme, request.META["HTTP_HOST"], invite_url)
        return redirect_url

def _get_provider_instance(provider, redirect_url):    
    if provider not in providers:
        raise Exception("The provider %s is not supported." % provider)

    client_id = getattr(settings, "%s_CLIENT_ID" % provider.upper(), None)
    client_secret = getattr(settings, "%s_CLIENT_SECRET" % provider.upper(), None)

    if not client_id:
        raise Exception("The provider %s is not supported." % provider)

    provider_class = providers[provider]
    return provider_class(client_id, client_secret, redirect_url)
__author__ = 'Adeel'
import urllib,urllib2,json
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
import string
import random
import json
class WydlWrapper(object):
    host = 'http://www.wdyl.com/profanity?'
    def get(self,params={}):
        url = str()
        try:
            url = WydlWrapper.host+urllib.urlencode(params)
            reply_raw = urllib2.urlopen(url).read()
            reply_json = json.loads(reply_raw)
            return reply_json
        except Exception as e:
            print e
    def get_error_message(self):
        return 'The alias you have chosen is inappropriate. '


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
    print 'Email sent'


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def check_string_valid(in_str):
    if in_str is None:
        return False
    elif in_str.isspace():
        return False
    elif len(in_str) == 0:
        return False
    else:
        return True
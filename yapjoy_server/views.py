__author__ = 'Adeel'
import requests
import json
from django.shortcuts import HttpResponse
from yapjoy.settings import DEBUG
def send_news(message):
    if not DEBUG:
        r = requests.post("https://server-yapjoy.herokuapp.com/api/post_news/", data={'code': 'Thi9sISt2-8HEYaPJ3oY7S-erVerC4ode_topo5stames6sage1','message':message})
        response = json.loads(r.text)
        if response['result'] == "success":
            return HttpResponse('News sent.')
        return HttpResponse('News sent failed.')
    else:
        return HttpResponse('News cannot be sent in debug mode.')


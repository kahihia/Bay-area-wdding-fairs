from django.db import models
from django.contrib.auth.models import User

class CSV_Event(models.Model):
    title = models.CharField(max_length=1000, null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CSV_UserEvents(models.Model):
    event = models.ForeignKey(CSV_Event)
    user = models.ForeignKey(User)
    csv_file = models.FileField(upload_to='events/csv')
    SHOW = "show"
    HIDE = "hide"
    STATUS_OPTIONS = (
        (SHOW, "Show"),
        (HIDE, "Hide"),
    )
    status = models.CharField(max_length=50, choices=STATUS_OPTIONS, default=SHOW)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class CSV_UserEventList(models.Model):
    event = models.ForeignKey(CSV_UserEvents)
    user_id = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=300, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


'''
import csv
import requests
import urllib2
from urllib import request
response = requests.urlopen(m.csv_file.url)
csv = response.read()
csvstr = str(csv).strip("b'")
lines = csvstr.split("\\n")
for line in lines:
    print line
with open(r.readim(), 'rU') as f:
    reader = csv.reader(f)
    next(reader, None)
    mylist = []

    for row in reader:
        print "inside row"
        print row[1]
'''

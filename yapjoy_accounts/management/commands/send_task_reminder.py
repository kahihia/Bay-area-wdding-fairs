from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from django.contrib.auth.models import User
from yapjoy_registration.models import *
from django.db.models import Q
from yapjoy_files.models import *
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from datetime import datetime, timedelta
class Command(NoArgsCommand):
    help = 'Sending Task Remainder'

    def handle_noargs(self, **options):
        tomorrow = datetime.now().date() + timedelta(days=1)
        # ------------------- interested vendors ------------------------
        tasks = SalesTasksEx.objects.select_related('exhibitor','sales').filter(dueDate__icontains=tomorrow)
        print "Tasks count: ", tasks.count()
        if tasks:
            for task in tasks:
                email = task.sales.email
                if email:
                    print email, task.dueDate ,task.subject, task.message
                    context = {
                        'message':"Dear %s,<br /><br />This is to remind you of the task assigned to you:<br /><br />Task Subject: %s<br />Task Message: %s<br />Due Date: %s<br />Lead/Contact: <a href='https://bayareaweddingfairs.herokuapp.com/crm/invoices/interested_detail/%s'>%s</a><br />Status: %s<br />Email: %s<br />Phone: %s<br /><br />This is a system generated message, please donot repond to this email.<br /><br />Best<br />Bay Area Wedding Fairs in collaboration with YapJoy."%(task.sales.get_full_name(),task.subject,task.message, task.dueDate,str(task.exhibitor.id), task.exhibitor.name, task.status, task.exhibitor.email, task.exhibitor.phone),
                        'title':"Bay Area Wedding Fairs - Task Reminder",
                        }
                    html_content = render_to_string('email/bawf_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives("BayAreaWeddingFairs Task Reminder", text_content, 'info@bayareaweddingfairs.com', [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
        # ------------------- contracted vendors ------------------------
        tasks_con = SalesTasks.objects.select_related('exhibitor','sales').filter(dueDate__icontains=tomorrow)
        print "Tasks count: ", tasks.count()
        if tasks_con:
            for task in tasks_con:
                email = task.sales.email
                if email:
                    print email, task.dueDate, task.subject, task.message
                    context = {
                        'message': "Dear %s,<br /><br />This is to remind you of the task assigned to you:<br /><br />Task Subject: %s<br />Due Date: %s<br />Lead/Contact: %s<br />Status: %s<br />Email: %s<br />Phone: %s<br /><br />This is a system generated message, please donot repond to this email.<br /><br />Best<br />Bay Area Wedding Fairs in collaboration with YapJoy." % (
                        task.sales.get_full_name(), task.subject, task.dueDate, task.exhibitor.name, task.status,
                        task.exhibitor.email, task.exhibitor.phone),
                        'title': "Bay Area Wedding Fairs - Task Reminder",
                    }
                    html_content = render_to_string('email/bawf_email.html', context=context)
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives("BayAreaWeddingFairs Task Reminder", text_content,
                                                 'info@bayareaweddingfairs.com', [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()


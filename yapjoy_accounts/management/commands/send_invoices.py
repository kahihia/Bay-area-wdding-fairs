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
class Command(NoArgsCommand):
    help = 'Sending Invoices'

    def handle_noargs(self, **options):
        invoices = InvoiceRegisterVendor.objects.select_related('register').filter(Q(is_sent_deposit==False)|Q(is_sent_balance1==False)|Q(is_sent_balance2==False)|Q(is_sent_balance3==False))
        for invoice in invoices:
            email = invoice.register.email
            if not invoice.is_sent_deposit:
                context = {
                    'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(invoice.deposit_code),
                    'title':"Bay Area Wedding Fairs Invoice",
                    }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                invoice.is_sent_deposit = True
                invoice.save()
            if not invoice.is_sent_balance1:
                context = {
                    'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(invoice.balance1_code),
                    'title':"Bay Area Wedding Fairs Invoice",
                    }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                invoice.balance1_code = True
                invoice.save()
            if not invoice.is_sent_balance2:
                context = {
                    'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(invoice.balance2_code),
                    'title':"Bay Area Wedding Fairs Invoice",
                    }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                invoice.balance2_code = True
                invoice.save()
            if not invoice.is_sent_balance3:
                context = {
                    'message':"Click on the following link to view the invoice <br /><br /><a href='https://www.yapjoy.com/crm/invoices/accept/%s' target='_blank' class='btn'>Open Invoice</a>"%(invoice.balance3_code),
                    'title':"Bay Area Wedding Fairs Invoice",
                    }
                html_content = render_to_string('email/bawf_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("BayAreaWeddingFairs Invoice", text_content, 'info@bayareaweddingfairs.com', [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                invoice.balance3_code = True
                invoice.save()
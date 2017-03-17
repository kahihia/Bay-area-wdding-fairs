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
from dateutil.relativedelta import relativedelta
from yapjoy_accounts.models import Transaction, TransactionHistory
import stripe
class Command(NoArgsCommand):
    help = 'Sending Invoices'

    def handle_noargs(self, **options):
        profiles = UserProfile.objects.filter(subscribed=True).select_related('user')
        today = datetime.now()
        for profile in profiles:
            try:
                user = profile.user
                # print user.email
                sub = SubscribedUsers.objects.get(user=user)
                # d1 = datetime.date.today()

                # d1 + relativedelta(months=1)
                if sub.subscription_date.date() + relativedelta(months=sub.no_of_months) < datetime.now().date():
                    print user.email, sub.subscription_date, sub.no_of_months
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    response = None
                    try:
                        response = stripe.Charge.create(
                            amount=100*sub.amount,  # Convert dollars into cents
                            currency="usd",
                            customer=profile.stripe_id,
                            description=user.email,
                        )
                        if response:
                            sub.no_of_months = 1
                            sub.subscription_date = datetime.now()
                            # sub.amount = 100
                            sub.save()
                            profile.subscribed = True
                            profile.save()
                            Transaction.objects.create(user=user, amount=str(sub.amount), status=Transaction.COMPLETED,
                                                       response=response,
                                                       transaction_id=response['balance_transaction'])
                            TransactionHistory.objects.create(user=user, event="Auto Resubscription.",
                                                              amount=sub.amount)
                            context = {
                                'message': "Dear %s<br /><br />Your subscription has been charged successfully.<br /><br />Thank you for using YapJoy." % (
                                user.get_full_name()),
                                'title': "Your YapJoy subscription is successfully recharged.",
                            }
                            html_content = render_to_string('email/generic_email.html', context=context)
                            text_content = strip_tags(html_content)
                            msg = EmailMultiAlternatives("YapJoy subscription is successfully charged.", text_content,
                                                         'info@yapjoy.com',
                                                         [profile.user.email,
                                                          ], bcc=['wasim@yapjoy.com','adeelpkpk@gmail.com'])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()
                    except Exception as e:
                        print e
                        profile.subscribed = False
                        profile.save()
                        context = {
                            'message': "Dear %s<br /><br />Your auto resubscription is failed due to the following reason:<br /><br />Reason: Your card was declined.<br /><br />Kindly visit YapJoy and recharge your subscription manually.." % (
                                user.get_full_name()),
                            'title': "Your YapJoy subscription is failed.",
                        }
                        html_content = render_to_string('email/generic_email.html', context=context)
                        text_content = strip_tags(html_content)
                        msg = EmailMultiAlternatives("YapJoy subscription is failed.", text_content,
                                                     'info@yapjoy.com',
                                                     [profile.user.email,
                                                        ], bcc=['wasim@yapjoy.com', 'adeelpkpk@gmail.com'])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    print response

            except Exception as e:
                profile.subscribed = False
                profile.save()
                context = {
                    'message':"Dear %s,<br /><br />Your subscription has been cancelled due to improper subscription.<br /><br />Our team is looking forward for the cancellation reason in detaiil.<br /><br />For any queries, kindly contact us at info@yapjoy.com."%(user.get_full_name()),
                    'title':"Your YapJoy subscription is cancelled.",
                    }
                html_content = render_to_string('email/generic_email.html', context=context)
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives("YapJoy subscription is cancelled.", text_content, 'info@yapjoy.com',  [profile.user.email,
                                                          ], bcc=['wasim@yapjoy.com','adeelpkpk@gmail.com'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()


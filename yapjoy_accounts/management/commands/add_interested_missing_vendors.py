from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_files.models import *
from dateutil import parser
from django.contrib.auth.models import User
class Command(NoArgsCommand):
    help = 'read and import csv for brige and groom'

    def handle_noargs(self, **options):
        your_list = None
        task_list = None
        print "read and import csv for brige and groom"
        with open('csv/Interested_vendors_11_11_2016/Notes_001-2.csv', 'rU') as f_notes:
            # print "script started"
            reader_notes = csv.reader(f_notes)
            your_list = list(reader_notes)
        with open('csv/Interested_vendors_11_11_2016/Tasks_001-2.csv', 'rU') as f_tasks:
            # print "script started"
            reader_task = csv.reader(f_tasks)
            task_list = list(reader_task)
        with open('csv/Interested_vendors_11_11_2016/Leads_001-2.csv', 'rU') as f:
            print "script started"
            reader = csv.reader(f)
            next(reader, None)
            mylist = []
            count = 0
            ln = 0
            bl = 0
            for row in reader:
                if row and not Register_Event_Interested.objects.filter(reference=str(row[0])).exists():


                    # with open('csv/Interested_vendors_11_11_2016/Notes_001-2.csv', 'rU') as f_notes:
                    email = row[6]
                    # print row[40]
                    print 'found: ',str(row[0])
                    user = None
                    try:
                        user = User.objects.get(email__iexact=email)
                    except Exception as e:
                        # print "Creating User"
                        user = User.objects.create(email=email, username=email)
                    reg = Register_Event_Interested.objects.create(
                        user=user,
                        name="%s %s"%(row[3], row[4]),
                        business_name=row[2],
                        phone=row[7],
                        email=email,
                        city=row[24],
                        zip=row[26],
                        website=row[10],
                        comments=row[40],
                        type=Register_Event_Interested.CONTRACTOR,
                        how_heard=row[17],
                        description=row[28],
                        category=row[37],
                        reference=str(row[0]),
                    )
                    try:
                        reg.created_at = parser.parse(row[20])
                        reg.save()
                    except Exception as e:
                        print "Datetime: ",e
                    #     # print "script started"
                    #       reader_notes = csv.reader(f_notes)
                    #     your_list = list(reader_notes)
                    #     next(reader_notes, None)
                    #     mylist = []
                    #     count = 0
                    #     ln = 0
                    #     bl = 0
                    # for row_tasks in task_list:
                    #     if row_tasks:
                    #         # print row_notes[4]
                    #         # if row[0] == "zcrm_1236681000000365357":
                    #         #     print 'zcrm_1236681000000365357', row[6]
                    #         if row[0] == row_tasks[5]:
                    #             print '-------------------------TASKS-----------------------------------'
                    #             print row[6]
                    #             print row_tasks[5]
                    # for row_notes in your_list:
                    #     if row_notes:
                    #         # print row_notes[4]
                    #         # if row[0] == "zcrm_1236681000000365357":
                    #         #     print 'zcrm_1236681000000365357', row[6]
                    #         if row[0] == row_notes[4]:
                    #             print '--------------------------NOTES------------------------------------'
                    #             print row[6]
                    #             print row_notes[3]
                                # count += 1
                                # print row[0]
                        # print count
                        #     if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[1]):
                        #         if User.objects.filter(email__iexact=row[1]).count() == 0:
                        #             user = User.objects.create(username=row[1], email=row[1])
                        #             count += 1
                        #             print user.email, count
                        #             # profile = user.userprofile
                        #             # profile
                        #         # if row[0]:
                        #         #     ln += 1
                        #         # if row[8]:
                        #         #     bl += 1
                        #         # print row[0], row[8], row[10]
                        #         # count += 1
                        # print count, ln, bl
                    count += 1
                    print count
                    # print row[0]
            print count
            #     if re.match("([^@|\s]+@[^@]+\.[^@|\s]+)",row[1]):
            #         if User.objects.filter(email__iexact=row[1]).count() == 0:
            #             user = User.objects.create(username=row[1], email=row[1])
            #             count += 1
            #             print user.email, count
            #             # profile = user.userprofile
            #             # profile
            #         # if row[0]:
            #         #     ln += 1
            #         # if row[8]:
            #         #     bl += 1
            #         # print row[0], row[8], row[10]
            #         # count += 1
            # print count, ln, bl
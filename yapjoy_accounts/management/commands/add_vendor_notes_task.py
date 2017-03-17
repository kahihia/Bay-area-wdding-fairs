from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify
import csv
import re
from yapjoy_files.models import *
from django.contrib.auth.models import User
from dateutil import parser
# parser.parse(convert)
def get_user(refID):
    user_list = None
    with open('csv/Interested_vendors_11_11_2016/Users_001-2.csv', 'rU') as f_users:
        # print "script started"
        reader_users = csv.reader(f_users)
        user_list = list(reader_users)
        for o in user_list:
            if o:
                if o[0] == refID:
                    user = User.objects.get(email__iexact=o[1])
                    return user
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
        # with open('csv/Interested_vendors_11_11_2016/Users_001-2.csv', 'rU') as f_notes:
        #     # print "script started"
        #     reader_notes = csv.reader(f_notes)
        #     your_list = list(reader_notes)
        with open('csv/Interested_vendors_11_11_2016/Tasks_001-2.csv', 'rU') as f_tasks:
            # print "script started"
            reader_task = csv.reader(f_tasks)
            task_list = list(reader_task)
        counter = Register_Event_Interested.objects.all().count()
        # for vendor in Register_Event_Interested.objects.all():
        #     SalesTasksEx.objects.filter(exhibitor=vendor).delete()
        for vendor in Register_Event_Interested.objects.filter(email__iexact="sybil@sybilstuttseventstyling.com"):
            counter = counter-1
            print counter
            # print "script started"
            # reader = csv.reader(f)
            # next(reader, None)
            mylist = []
            count = 0
            ln = 0
            bl = 0
            # for row in reader:
            if vendor.reference:


                # with open('csv/Interested_vendors_11_11_2016/Notes_001-2.csv', 'rU') as f_notes:
                # print row[40]

                #     # print "script started"
                #     reader_notes = csv.reader(f_notes)
                #     your_list = list(reader_notes)
                #     next(reader_notes, None)
                #     mylist = []
                #     count = 0
                #     ln = 0
                #     bl = 0
                if True:
                    for row_tasks in task_list:
                        if row_tasks and not row_tasks[14] == "Reminder":
                            # SalesTasksEx.objects.filter(exhibitor=vendor).delete()
                            # print vendor.email

                            # print row_tasks[5], vendor.reference
                            if row_tasks[5] == vendor.reference and row_tasks[14]:
                                print row_tasks[8], vendor.reference, vendor.email, row_tasks[14], parser.parse(str(row_tasks[14])).date()
                                print 'creating: ',parser.parse(str(row_tasks[10])).date()
                                task_o = SalesTasksEx.objects.create(exhibitor=vendor,
                                                                     sales=get_user(row_tasks[8]),
                                                                     subject=row_tasks[2],
                                                                     message=row_tasks[12],
                                                                     dueDate=parser.parse(str(row_tasks[14])).date(),

                                                                     )
                                task_o.created_at = parser.parse(row_tasks[10])
                                task_o.save()
                                print task_o.id
                # count += 1
                # print count
                        # if vendor.reference == row_tasks[5]:
                            # print '-------------------------TASKS-----------------------------------'
                #             print row[6]
                #             print row_tasks[5]
                # for row_notes in your_list:
                #     if row_notes:
                #
                #         # print row_notes[4]
                #         # if row[0] == "zcrm_1236681000000365357":
                #         #     print 'zcrm_1236681000000365357', row[6]
                #         # print row_notes[4], vendor.reference, vendor.email
                #         if vendor.reference == row_notes[4]:
                #             print '--------------------------NOTES------------------------------------'
                #             # print row[6]
                #             print get_user(row_notes[5])
                #             print row_notes[5]
                #             count += 1
                #             notex = NotesEx.objects.create(
                #                 exhibitor = vendor,
                #                 note_writer = get_user(row_notes[5]),
                #                 note = row_notes[3],
                #
                #             )
                #             notex.created_at = parser.parse(row_notes[7])
                #             notex.save()
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
            # count += 1
            # print count, vendor.id
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
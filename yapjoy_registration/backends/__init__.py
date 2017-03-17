__author__ = 'Adeel'

# from django.core.management.base import NoArgsCommand
# from django.template.defaultfilters import slugify
# import csv
# from django.db.models import Q
# from django.contrib.auth.models import User
# with open('B_G_List.csv', 'rU') as f:
#     reader = csv.reader(f)
#     #next(reader, None)
#     mylist = []
#     count = 0
#     for row in reader:
#         try:
#             u = User.objects.get(username__iexact=row[2])
#             print row[2]
#         except:
#             pass
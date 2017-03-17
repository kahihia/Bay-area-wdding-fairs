from django.shortcuts import render
from .models import *
def view_csv(request):
    user = request.user
    events = CSV_UserEvents.objects.filter(user=user)
    return render(request, 'vendroid/csv/view_csv.html',{
        'events':events,
    })
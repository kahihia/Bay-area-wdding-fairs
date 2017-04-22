from django.shortcuts import render
from .models import *

from yapjoy_files.models import Event_fairs
from collections import OrderedDict
from datetime import datetime

def Index(request):
    return render(request, "bayareaweddingfairs/site/home/home.html")

def ShopVendors(request):
    vendorShopsList = []
    vendorShops = ShopVendor.objects.all()
    for shop in vendorShops:
        shopItemList = ShopVendorsItem.objects.filter(shopVendors=shop).order_by('created_at')
        vendorShop = {
            'shop': shop,
            'itemsList': shopItemList
        }
        vendorShopsList.append(vendorShop)

    context = {
        'vendorShops': vendorShops,
        'vendorShopsList': vendorShopsList
    }
    return render(request, "bayareaweddingfairs/shopVendors/index.html", context)

def OurShows(request):
    events_list = Event_fairs.objects.filter(date__gte=datetime.now(), is_expired=False)
    events = sort_months(events_list)
    return render(request, "bayareaweddingfairs/ourShows/index.html",{
        'events':events,
    })

def sort_months(events):
    January, February, March, April, May, June, July, August, September, October, November, December = ([] for i in range(12))
    list_months = ['', January, February, March, April, May, June, July, August, September, October, November, December]
    for event in events:
        list_months[event.date.month].append(event)
    return list_months
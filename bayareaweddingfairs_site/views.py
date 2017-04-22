from django.shortcuts import render
from .models import *


def Index(request):
    return render(request, "bayareaweddingfairs/site/index/index.html")


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
    # return render(request, "bayareaweddingfairs/site/index/shopVendors.html", context)
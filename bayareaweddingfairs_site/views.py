from django.shortcuts import render

def Index(request):
    return render(request, "bayareaweddingfairs/site/index/index.html")

def ShopVendors(request):
    return render(request, "bayareaweddingfairs/shopVendors/index.html")
from django.shortcuts import render

def Index(request):
    return render(request, "bayareaweddingfairs/site/index/index.html")

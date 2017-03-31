from django.shortcuts import render

# Create your views here.
def IndexMarket(request):
    return render(request, "bayareaweddingfairs/index.html")

def donateMarket(request):
    return render(request, "bayareaweddingfairs/donate.html")
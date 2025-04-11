from django.shortcuts import render

def home_api(request):
    return render(request, 'api/index.html')
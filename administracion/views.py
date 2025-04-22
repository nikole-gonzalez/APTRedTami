
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'administracion/index.html')

def admin_index(request):
    return render(request, 'administracion/index.html')

def cesfam_index(request):
    return render(request, 'cesfam/index_c.html')





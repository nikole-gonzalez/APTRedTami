from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
from . import views

urlpatterns = [
    path('', views.home, name='admin-index'),
    path('admin_index/', views.admin_index, name='admin_index'),
   
]
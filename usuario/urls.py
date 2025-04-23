from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home_usuario, name='usuario-index'),
    path('usuario_index/', views.usuario_index, name='usuario_index'),


]
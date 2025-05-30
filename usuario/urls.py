from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home_usuario, name='usuario-index'),
    path('usuario_index/', views.usuario_index, name='usuario_index'),

    #Página informativa
    path('pagina_informativa/', views.pag_informativa, name='pag_informativa'),
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('panel_usuario/', views.panel_usuario, name='panel_usuario'),
    path('eliminar_datos/', views.eliminar_datos_usuario, name='eliminar_datos_usuario'),
    path('agendamiento/', views.agendamiento, name='agendamiento'),

]
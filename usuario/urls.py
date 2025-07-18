from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home_usuario, name='usuario-index'),
    path('usuario_index/', views.usuario_index, name='usuario_index'),

    #Página informativa
    path('pagina_informativa/', views.pagina_informativa, name='pagina_informativa'),
    path('panel_usuario/', views.panel_usuario, name='panel_usuario'),
    path('eliminar_datos/', views.eliminar_datos_usuario, name='eliminar_datos_usuario'),
    path('agendamiento/', views.agendamiento, name='agendamiento'),
    path('respuestas_usuarias/', views.visualizar_resp_usuarias, name='respuestas_usuarias')

]
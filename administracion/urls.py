from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
from . import views

urlpatterns = [
    path('', views.home, name='admin-index'),
    path('admin_index/', views.admin_index, name='admin_index'),
    path('cesfam_index/', views.cesfam_index, name='cesfam_index'),
   

    path('respuestas/', views.respuestas, name='respuestas'),
    path('reportes/', views.reportes, name='reportes'),
    path('apis/', views.apis, name='apis'),
    path('mensaje/', views.mensaje, name='mensajes'),

    path('datos_perfil/', views.datos_perfil, name="datos_perfil"),
    path('tamizaje/', views.tamizaje, name="tamizaje"),
    path('opc_vis_FRM/', views.opc_vis_FRM, name="opc_vis_FRM"),
    path('opc_vis_FRNM/', views.opc_vis_FRNM, name="opc_vis_FRNM"),
    path('opc_vis_DS/', views.opc_vis_DS, name="opc_vis_DS"),
    path('preg_especialista/', views. preg_especialista, name="preg_especialista"),
    path('listado_priorizado/', views.listado_priorizado, name="listado_priorizado"),
   
]

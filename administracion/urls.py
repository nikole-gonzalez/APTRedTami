from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
from . import views

urlpatterns = [
    path('', views.home, name='admin-index'),
    path('admin_index/', views.admin_index, name='admin_index'),
    path('cesfam_index/', views.cesfam_index, name='cesfam_index'),
   
    #Opciones Home
    path('respuestas/', views.respuestas, name='respuestas'),
    path('reportes/', views.reportes, name='reportes'),
    path('apis/', views.apis, name='apis'),
    path('mensaje/', views.mensaje, name='mensajes'),
    path('gestion_usuarios/', views.gestion_usuarios, name="gestion_usuarios"),

    #Opciones respuestas
    path('datos_perfil/', views.datos_perfil, name="datos_perfil"),
    path('tamizaje/', views.tamizaje, name="tamizaje"),
    path('opc_vis_FRM/', views.opc_vis_FRM, name="opc_vis_FRM"),
    path('opc_vis_FRNM/', views.opc_vis_FRNM, name="opc_vis_FRNM"),
    path('opc_vis_DS/', views.opc_vis_DS, name="opc_vis_DS"),
    path('preg_especialista/', views. preg_especialista, name="preg_especialista"),
    path('listado_priorizado/', views.listado_priorizado, name="listado_priorizado"),

    #Opciones de factores
    path('datos_DS1/', views.datos_DS1, name="datos_DS1"),
    path('datos_DS2/', views.datos_DS2, name="datos_DS2"),
    path('datos_FRM1/', views.datos_FRM1, name="datos_FRM1"),
    path('datos_FRM2/', views.datos_FRM2, name="datos_FRM2"),
    path('datos_FRNM1/',views.datos_FRNM1, name="datos_FRNM1"),
    path('datos_FRNM2/', views.datos_FRNM2, name="datos_FRNM2"),

    #Desacargar en excel
    path('crear_excel_datos_tamizaje/', views.crear_excel_datos_tamizaje, name="crear_excel_datos_tamizaje"),
    path('crear_excel_datos_frm1/', views.crear_excel_datos_frm1, name="crear_excel_datos_frm1"),
    path('crear_excel_datos_frnm1/', views.crear_excel_datos_frnm1, name="crear_excel_datos_frnm1"),
    path('crear_excel_datos_ds1/', views.crear_excel_datos_ds1, name="crear_excel_datos_ds1"),
]

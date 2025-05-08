
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

import base64
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import requests
import numpy as np

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, F, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from collections import Counter
from django.db.models.functions import ExtractYear
from django.db.models.functions import TruncDate


from openpyxl import Workbook

from .models import *

from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

from django.views.decorators.csrf import csrf_exempt
import json
import locale 

import logging

locale.setlocale(locale.LC_TIME, 'es_ES')

def home(request):
    return render(request, 'administracion/index.html')

@login_required
def admin_index(request):
    return render(request, 'administracion/index.html')

def cesfam_index(request):
    return render(request, 'cesfam/index_c.html')

@login_required
def respuestas(request):
    return render(request, 'administracion/respuestas.html')

@login_required
def apis(request):
    return render(request, 'administracion/apis.html')

@login_required
def mensaje(request):
    return render(request, 'administracion/mensaje.html')

@login_required
def gestion_usuarios(request):
    return render(request, 'administracion/gestion_usuarios.html')

@login_required
def opc_vis_FRM(request):
    return render(request, 'administracion/opc_vis_FRM.html')

@login_required
def opc_vis_FRNM(request):
    return render(request, 'administracion/opc_vis_FRNM.html')

@login_required
def datos_FRNM1(request):
    return render(request, 'administracion/datos_FRNM1.html')

@login_required
def datos_FRNM2(request):
    return render(request, 'administracion/datos_FRNM2.html')

@login_required
def datos_FRM1(request):
    return render(request, 'administracion/datos_FRM1.html')

@login_required
def datos_FRM2(request):
    return render(request, 'administracion/datos_FRM2.html')

@login_required
def opc_vis_DS(request):
    return render(request, 'administracion/opc_vis_DS.html')

@login_required
def datos_DS1(request):
    return render(request, 'administracion/datos_DS1.html')

@login_required
def datos_DS2(request):
    return render(request, 'administracion/datos_DS2.html')

@login_required
def preg_especialista(request):
    return render(request, 'administracion/preg_especialista.html')

@login_required
def listado_priorizado (request):
    return render(request, 'administracion/listado_priorizado.html')


# ------------------------------------------------------ #
# ---------------------- Reportes ---------------------- #
# ------------------------------------------------------ #

# Configuración global para fuentes de gráficos

@login_required
def reportes(request):
    grafico_genero = generar_grafico_personas_por_genero()
    grafico_comuna = generar_grafico_ingresos_por_comuna()
    grafico_pap_tres_anios = generar_grafico_realizado_pap_tres_anios()
    grafico_escolaridad = generar_grafico_escolaridad()
    grafico_anio_nac = generar_grafico_anio_nacimiento()
    grafico_resp_diarias = generar_grafico_respuestas_por_dia()
    grafico_usuarias_edad = generar_grafico_usuario_por_edad()

    data = {
        "imagen_base64_personas_por_genero": grafico_genero,
        "imagen_base64_ingresos_por_comuna": grafico_comuna,
        "imagen_base64_realizado_pap_tres_anios": grafico_pap_tres_anios,
        "imagen_base64_escolaridad": grafico_escolaridad,
        "imagen_base64_anio_nacimiento": grafico_anio_nac,
        "imagen_base64_resp_por_dia": grafico_resp_diarias,
        "imagen_base64_usuarias_por_edad": grafico_usuarias_edad,
        "hay_datos": grafico_genero or grafico_comuna or grafico_pap_tres_anios or grafico_escolaridad
            or grafico_anio_nac or grafico_resp_diarias or grafico_usuarias_edad
    }
    return render(request, 'administracion/reportes.html', data)

# Función para convertir los gráficos a base64

def convertir_grafico_a_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

#Función para calcular la edad 

def calcular_edad(fecha_nacimiento):
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

plt.rcParams['font.family'] = 'sans-serif'  
plt.rcParams['font.sans-serif'] = 'Calibri' 
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] =20
plt.rcParams['axes.labelsize']= 13
plt.rcParams['axes.labelpad']=10

def generar_grafico_personas_por_genero():
    respuestas = RespFRNM.objects.filter(id_opc_frnm__id_opc_frnm__in=[1, 2, 3])

    if not respuestas.exists():
        return None

    contador = Counter(respuestas.values_list('id_opc_frnm__id_opc_frnm', flat=True))

    generos = []
    cantidades = []

    for genero_id in [1, 2, 3]:
        try:
            genero = OpcFRNM.objects.get(id_opc_frnm=genero_id)
            generos.append(genero.opc_resp_frnm)
            cantidades.append(contador.get(genero_id, 0))
        except OpcFRNM.DoesNotExist:
            continue

    if not any(cantidades):
        return None

    colores = {'Masculino': '#79addc', 'Femenino': '#EFB0C9', 'Otro': '#A5F8CE'}

    plt.figure(figsize=(8, 6))

    plt.bar(generos, cantidades, color=[colores.get(g, '#CCCCCC') for g in generos])

    for i in range(len(generos)):
        plt.text(i, cantidades[i], str(cantidades[i]), ha='center', va='bottom')

    plt.xlabel("Género")
    plt.ylabel("Número de Personas")
    plt.title("Ingresos por Género", pad=20)

    return convertir_grafico_a_base64()

def generar_grafico_ingresos_por_comuna():
    
    respuestas = RespFRNM.objects.filter(id_opc_frnm__id_opc_frnm__in=[1, 3])

    datos_agrupados = (
        respuestas
        .values('id_usuario__cod_comuna__nombre_comuna')
        .annotate(total=Count('id_resp_frnm'))
        .order_by('id_usuario__cod_comuna__nombre_comuna')
    )

    comunas = [dato['id_usuario__cod_comuna__nombre_comuna'] for dato in datos_agrupados]
    total_ingresos = [dato['total'] for dato in datos_agrupados]

    if not total_ingresos:
        return None  

    # Crear gráfico circular
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        total_ingresos,
        labels=comunas,
        autopct=lambda pct: f"{pct:.1f}%\n{int(pct/100 * sum(total_ingresos) + 0.5)} ingresos",
        startangle=90
    )
    ax.axis('equal')
    ax.set_title('Distribución de Ingresos por Comuna', pad=20)

    # Ajustar el tamaño del texto
    for text, autotext in zip(texts, autotexts):
        text.set(size=8)
        autotext.set(size=8)

    return convertir_grafico_a_base64()


def generar_grafico_realizado_pap_tres_anios():
    
    manychat_ids = RespFRNM.objects.filter(
        id_opc_frnm__id_opc_frnm__in=[1, 3]
    ).values_list('id_manychat', flat=True)

   
    respuestas_tm = RespTM.objects.filter(
        id_manychat__in=manychat_ids,
        id_opc_tm__id_opc_tm__in=[1, 2, 3]
    )

    contador = Counter(respuestas_tm.values_list('id_opc_tm__id_opc_tm', flat=True))

    if not contador:
        return None

    labels = []
    sizes = []
    counts = []

    for id_opc_tm in [1, 2, 3]:
        try:
            opcion = OpcTM.objects.get(id_opc_tm=id_opc_tm)
            cantidad = contador.get(id_opc_tm, 0)
            labels.append(opcion.opc_resp_tm)
            sizes.append(cantidad)
            counts.append(f"{opcion.opc_resp_tm} - {cantidad}")
        except OpcTM.DoesNotExist:
            continue

    # Crear gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct='%1.1f%%', startangle=90,
        colors=['#79addc', '#EFB0C9', '#A5F8CE']
    )
    
    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('¿Te has realizado una PAP en los últimos 3 años?', pad=20)

    return convertir_grafico_a_base64()

def generar_grafico_escolaridad():
   
    manychat_ids = RespFRNM.objects.filter(
        id_opc_frnm__id_opc_frnm__in=[1, 3]
    ).values_list('id_manychat', flat=True)

    respuestas_ds = RespDS.objects.filter(
        id_manychat__in=manychat_ids,
        id_opc_ds__id_opc_ds__in=[1, 2, 3]
    )

    contador = Counter(respuestas_ds.values_list('id_opc_ds__id_opc_ds', flat=True))

    if not contador:
        return None

    labels = []
    sizes = []
    counts = []

    for id_opc_ds in [1, 2, 3]:
        try:
            opcion = OpcDS.objects.get(id_opc_ds=id_opc_ds)
            cantidad = contador.get(id_opc_ds, 0)
            labels.append(opcion.opc_resp_ds)
            sizes.append(cantidad)
            counts.append(f"{opcion.opc_resp_ds} - {cantidad}")
        except OpcDS.DoesNotExist:
            continue

    # Crear gráfico circular
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        colors=['#79addc', '#EFB0C9', '#A5F8CE']
    )

    ax.legend(wedges, counts, title="Respuestas", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Nivel de estudio usuarias', pad=20)

    return convertir_grafico_a_base64()

def generar_grafico_anio_nacimiento():
    
    manychat_ids = RespFRNM.objects.filter(
        id_opc_frnm__id_opc_frnm__in=[1, 3]
    ).values_list('id_manychat', flat=True)

    datos = (
        Usuario.objects
        .filter(id_manychat__in=manychat_ids)
        .annotate(anio=ExtractYear('fecha_nacimiento'))
        .values('anio')
        .annotate(cantidad=Count('id_manychat'))
        .order_by('anio')
    )

    anios = [dato['anio'] for dato in datos]
    cantidades = [dato['cantidad'] for dato in datos]

    if not anios:
        return None

    plt.figure(figsize=[18, 8])
    plt.bar(anios, cantidades, color="#79addc")
    plt.xlabel("Año de Nacimiento")
    plt.ylabel("Número de Usuarios")
    plt.title("Usuarias por Año de Nacimiento", pad=20)
    plt.xticks(range(min(anios), max(anios)+1, 1), rotation=90)

    for anio, cantidad in zip(anios, cantidades):
        plt.text(anio, cantidad, str(cantidad), ha='center', va='bottom')

    return convertir_grafico_a_base64()

def generar_grafico_respuestas_por_dia():
   
    manychat_ids = RespFRNM.objects.filter(
        id_opc_frnm__id_opc_frnm__in=[1, 3]
    ).values_list('id_manychat', flat=True)

    datos = (
        Usuario.objects
        .filter(id_manychat__in=manychat_ids)
        .annotate(fecha=TruncDate('fecha_ingreso'))
        .values('fecha')
        .annotate(cantidad=Count('id_manychat'))
        .order_by('fecha')
    )

    fechas = [dato['fecha'].strftime("%d-%m-%Y") for dato in datos]
    cantidades = [dato['cantidad'] for dato in datos]

    if not fechas:
        return None

    plt.figure(figsize=[14, 6])
    plt.plot(fechas, cantidades, marker="o", linestyle="-", color="#79addc")
    plt.xlabel("Fecha de Respuesta")
    plt.ylabel("Número de Respuestas")
    plt.title("Respuestas por Día", pad=20)
    plt.xticks(rotation=90)
    plt.tight_layout()

    for fecha, cantidad in zip(fechas, cantidades):
        plt.annotate(f"{cantidad}", (fecha, cantidad), textcoords="offset points", xytext=(0,10), ha='center')

    return convertir_grafico_a_base64()

def generar_grafico_usuario_por_edad():
    usuarios = Usuario.objects.filter(
        respfrnm__id_opc_frnm=1
    ).values_list('fecha_nacimiento', flat=True)

    # Calcular edades
    edades = [calcular_edad(fn) for fn in usuarios if fn]
    
    if not edades:
        return None

    # Contar ocurrencias por edad
    contador = Counter(edades)
    edades_ordenadas = sorted(contador.keys())
    cantidades = [contador[edad] for edad in edades_ordenadas]

    # Crear gráfico
    plt.figure(figsize=[18, 8])
    plt.bar(edades_ordenadas, cantidades, color="#79addc")
    plt.xlabel("Edad")
    plt.ylabel("Número de Usuarias")
    plt.title("Usuarias por edad", pad=20)
    
    if edades_ordenadas:
        plt.xticks(range(min(edades_ordenadas), max(edades_ordenadas) + 1, 1))

    for edad, cantidad in zip(edades_ordenadas, cantidades):
        plt.text(edad, cantidad, str(cantidad), ha='center', va='bottom')

    return convertir_grafico_a_base64()

# ------------------------------------------------------------------ #
# ---------------------- Respuestas Usuarias ----------------------- #
# ------------------------------------------------------------------ #

def ajustar_ancho_columnas(ws):
  
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            try:
                if cell.value: 
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        ws.column_dimensions[col_letter].width = max_length + 2

def background_colors(ws):

    color = "00a0b3a8" 
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    for cell in ws[1]: 
        cell.fill = fill

@login_required
def datos_perfil(request):
    Datos = Usuario.objects.all().order_by("-fecha_ingreso")
    data = {
        "Datos": Datos,
    }
    return render(request, "administracion/datos_perfil.html", data)

# ------------------ #
# ---- Tamizaje ---- #
# ------------------ #

@login_required
def tamizaje(request):
    Datos = RespTM.objects.select_related(
        "id_opc_tm", "id_opc_tm__id_preg_tm", "id_manychat"
    ).values(
        "id_resp_tm",
        "id_opc_tm__id_preg_tm__preg_tm",
        "id_opc_tm__opc_resp_tm",
        "fecha_respuesta_tm",
        "id_usuario__rut_usuario",
        "id_usuario__dv_rut"
    ).order_by("-fecha_respuesta_tm")

    data = {
        "Datos": Datos,
    }
    return render(request, 'administracion/tamizaje.html', data)

def crear_excel_datos_tamizaje(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados Tamizaje"

    # Encabezados
    ws.append(['Rut', 'Pregunta', 'Respuesta', 'Fecha Respuesta', 'Tipo'])

    # Obtener datos
    respuestas = RespTM.objects.select_related(
        'id_opc_tm__id_preg_tm', 'id_usuario'
    ).values(
        'id_usuario__rut_usuario',
        'id_usuario__dv_rut',
        'id_opc_tm__id_preg_tm__preg_tm',
        'id_opc_tm__opc_resp_tm',
        'fecha_respuesta_tm'
    ).order_by('-fecha_respuesta_tm')

    for r in respuestas:
        fecha = r['fecha_respuesta_tm']
        fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S') if fecha else ''
        
        ws.append([
            f"{r['id_usuario__rut_usuario']}-{r['id_usuario__dv_rut']}",
            r['id_opc_tm__id_preg_tm__preg_tm'],
            r['id_opc_tm__opc_resp_tm'],
            fecha_str,
            'TM'
        ])

    ajustar_ancho_columnas(ws)
    background_colors(ws)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename="datos_tamizaje.xlsx"'
    
    wb.save(response)
    return response

# ------------- #
# ---- FRM ---- #
# ------------- #

@login_required
def datos_FRM1(request):
    Datos = RespFRM.objects.select_related(
        "id_opc_frm", "id_opc_frm__id_preg_frm", "id_manychat"
    ).values(
        "id_resp_frm",
        "id_opc_frm__id_preg_frm__preg_frm",
        "id_opc_frm__opc_resp_frm",
        "fecha_respuesta_frm",
        "id_usuario__rut_usuario",
        "id_usuario__dv_rut"
    ).order_by("-fecha_respuesta_frm")

    data = {
        "Datos": Datos,
    }
    return render(request, "administracion/datos_FRM1.html", data)

def crear_excel_datos_frm1(request):
    wb = Workbook()
    ws_FRM_V1 = wb.active
    ws_FRM_V1.title = "Factores de riesgo modificables"

    ws_FRM_V1.append(['Rut', 'Pregunta', 'Respuesta', 'Fecha Respuesta'])

    respuestas = RespFRM.objects.select_related(
        'id_opc_frm__id_preg_frm', 'id_usuario'
    ).values(
        'id_usuario__rut_usuario',
        'id_usuario__dv_rut',
        'id_opc_frm__id_preg_frm__preg_frm',
        'id_opc_frm__opc_resp_frm',
        'fecha_respuesta_frm'
    ).order_by('id_usuario__rut_usuario')

    for r in respuestas:
        fecha = r['fecha_respuesta_frm']
        ws_FRM_V1.append([
            f"{r['id_usuario__rut_usuario']}-{r['id_usuario__dv_rut']}",
            r['id_opc_frm__id_preg_frm__preg_frm'],
            r['id_opc_frm__opc_resp_frm'],
            fecha.strftime('%Y-%m-%d %H:%M:%S') if fecha else ''
        ])

    ajustar_ancho_columnas(ws_FRM_V1)
    background_colors(ws_FRM_V1)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="FactoresMod_V1.xlsx"'
    wb.save(response)
    return response

# -------------- #
# ---- FRNM ---- #
# -------------- #

@login_required
def datos_FRNM1(request):
    Datos = RespFRNM.objects.select_related(
        "id_opc_frnm", "id_opc_frnm__id_preg_frnm", "id_manychat"
    ).values(
        "id_resp_frnm",
        "id_opc_frnm__id_preg_frnm__preg_frnm",
        "id_opc_frnm__opc_resp_frnm",
        "fecha_respuesta_frnm",
        "id_usuario__rut_usuario",
        "id_usuario__dv_rut"
    ).order_by("-fecha_respuesta_frnm")

    data = {
        "Datos": Datos,
    }
    return render(request, "administracion/datos_FRNM1.html", data)

def crear_excel_datos_frnm1(request):
    wb = Workbook()
    ws_FRNM_V1 = wb.active
    ws_FRNM_V1.title = "Riesgos no modificables"

    ws_FRNM_V1.append(['Rut', 'Pregunta', 'Respuesta', 'Fecha Respuesta'])

    respuestas = RespFRNM.objects.select_related(
        'id_opc_frnm__id_preg_frnm', 'id_usuario'
    ).values(
        'id_usuario__rut_usuario',
        'id_usuario__dv_rut',
        'id_opc_frnm__id_preg_frnm__preg_frnm',
        'id_opc_frnm__opc_resp_frnm',
        'fecha_respuesta_frnm'
    ).order_by('id_usuario__rut_usuario')

    for r in respuestas:
        fecha = r['fecha_respuesta_frnm']
        ws_FRNM_V1.append([
            f"{r['id_usuario__rut_usuario']}-{r['id_usuario__dv_rut']}",
            r['id_opc_frnm__id_preg_frnm__preg_frnm'],
            r['id_opc_frnm__opc_resp_frnm'],
            fecha.strftime('%Y-%m-%d %H:%M:%S') if fecha else ''
        ])

    # Aplicar formatos (funciones ya existentes)
    ajustar_ancho_columnas(ws_FRNM_V1)
    background_colors(ws_FRNM_V1)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="FactoresNoMod_V1.xlsx"'
    wb.save(response)
    return response

# ------------ #
# ---- DS ---- #
# ------------ #

@login_required
def datos_DS1(request):
    Datos = RespDS.objects.select_related(
        "id_opc_ds", "id_opc_ds__id_preg_ds", "id_manychat"
    ).values(
        "id_resp_ds",
        "id_opc_ds__id_preg_ds__preg_ds",
        "id_opc_ds__opc_resp_ds",
        "fecha_respuesta_ds",
        "id_usuario__rut_usuario",
        "id_usuario__dv_rut"
    ).order_by("-fecha_respuesta_ds")

    data = {
        "Datos": Datos,
    }
    return render(request, "administracion/datos_DS1.html", data)

def crear_excel_datos_ds1(request):
    wb = Workbook()
    ws_DS_V1 = wb.active
    ws_DS_V1.title = "Determinantes sociales"

    ws_DS_V1.append(['Rut', 'Pregunta', 'Respuesta', 'Fecha Respuesta'])

    respuestas = RespDS.objects.select_related(
        'id_opc_ds__id_preg_ds', 'id_usuario'
    ).values(
        'id_usuario__rut_usuario',
        'id_usuario__dv_rut',
        'id_opc_ds__id_preg_ds__preg_ds',
        'id_opc_ds__opc_resp_ds',
        'fecha_respuesta_ds'
    ).order_by('id_usuario__rut_usuario')

    for r in respuestas:
        fecha = r['fecha_respuesta_ds']
        ws_DS_V1.append([
            f"{r['id_usuario__rut_usuario']}-{r['id_usuario__dv_rut']}",
            r['id_opc_ds__id_preg_ds__preg_ds'],
            r['id_opc_ds__opc_resp_ds'],
            fecha.strftime('%Y-%m-%d %H:%M:%S') if fecha else ''
        ])

    # Aplicar formatos (funciones ya existentes)
    ajustar_ancho_columnas(ws_DS_V1)
    background_colors(ws_DS_V1)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="DeterminantesSociales_V1.xlsx"'
    wb.save(response)
    return response
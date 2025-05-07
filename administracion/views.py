
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
def datos_perfil(request):
    return render(request, 'administracion/datos_perfil.html')

@login_required
def tamizaje(request):
    return render(request, 'administracion/tamizaje.html')

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

    data = {
        "imagen_base64_personas_por_genero": grafico_genero,
        "imagen_base64_ingresos_por_comuna": grafico_comuna,
        "imagen_base64_realizado_pap_tres_anios": grafico_pap_tres_anios,
        "imagen_base64_escolaridad": grafico_escolaridad,
        "hay_datos": grafico_genero or grafico_comuna or grafico_pap_tres_anios or grafico_escolaridad
    }
    return render(request, 'administracion/reportes.html', data)

# Función para convertir los gráficos a base64

def convertir_grafico_a_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

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

    if not any(cantidades):  # No hay datos reales
        return None

    # Crear gráfico...
    colores = {'Masculino': '#79addc', 'Femenino': '#EFB0C9', 'Otro': '#A5F8CE'}
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

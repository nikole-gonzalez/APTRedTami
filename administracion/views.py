
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

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
def reportes(request):
    return render(request, 'administracion/reportes.html')

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
"""
plt.rcParams['font.family'] = 'sans-serif'  
plt.rcParams['font.sans-serif'] = 'Calibri' 
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] =20
plt.rcParams['axes.labelsize']= 13
plt.rcParams['axes.labelpad']=10

# Función para convertir los gráficos a base64
"""
"""
def convertir_grafico_a_base64():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

#Así se usa
imagen_base64 = convertir_grafico_a_base64()
return imagen_base64
"""
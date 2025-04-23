
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'administracion/index.html')

def admin_index(request):
    return render(request, 'administracion/index.html')

def cesfam_index(request):
    return render(request, 'cesfam/index_c.html')





def respuestas(request):
    return render(request, 'administracion/respuestas.html')

@login_required
def reportes(request):
    return render(request, 'administracion/reportes.html')

def apis(request):
    return render(request, 'administracion/apis.html')

def mensaje(request):
    return render(request, 'administracion/mensaje.html')

def datos_perfil(request):
    return render(request, 'administracion/datos_perfil.html')

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
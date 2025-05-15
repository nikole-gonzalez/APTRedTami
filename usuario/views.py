from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from administracion.models import *
from usuario.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

def home_usuario(request):
    return render(request, 'usuario/index.html')

@login_required
def usuario_index(request):
    try:
        perfil = request.user.perfilusuario
    except ObjectDoesNotExist:
        return render(request, 'usuario/usuario_sin_perfil.html', {
            'mensaje': 'Tu cuenta no tiene un perfil asignado. Contacta con el administrador.'
        }, status=403)

    return render(request, 'usuario/index.html', {
        'perfil': perfil
    })

def pag_informativa(request):
    return render(request, 'usuario/informativo.html')

def registro_usuario(request):
    return render(request, 'usuario/registro.html')

@login_required
def agendamiento(request):
    return render(request, 'usuario/agendamiento.html')

@login_required
def panel_usuario(request):
    try:
        perfil = request.user.perfilusuario
    except ObjectDoesNotExist:
        return render(request, 'usuario/usuario_sin_perfil.html', {
            'mensaje': 'Tu cuenta no tiene un perfil asignado. Contacta con el administrador.'
        }, status=403)

    if perfil.tipo_usuario == 'paciente':
        return render(request, 'usuario/panel_usuario.html', {
            'perfil': perfil
        })

    elif perfil.tipo_usuario == 'administrador':
        return redirect('/admin_index/')

    return redirect('login')

@login_required
def agendamiento(request):
    try:
        perfil = request.user.perfilusuario
        usuario_sist = perfil.usuario_sist
        agendamientos = Agenda.objects.filter(id_manychat=usuario_sist).order_by('-fecha_atencion') if usuario_sist else []
    except ObjectDoesNotExist:
        return render(request, 'usuario/usuario_sin_perfil.html', {
            'mensaje': 'Tu cuenta no tiene un perfil asignado. Contacta con el administrador.'
        }, status=403)

    return render(request, 'usuario/agendamiento.html', {
        'perfil': perfil,
        'agendamientos': agendamientos
    })

@login_required
def eliminar_datos_usuario(request):
    if request.method == 'POST':
        user = request.user

        try:
            perfil = user.perfilusuario
            
            usuario_sist = perfil.usuario_sist
            
            if usuario_sist:
                usuario_sist.delete()
            
            perfil.delete()
        except PerfilUsuario.DoesNotExist:
            pass

        user.delete()

        messages.success(request, "Se ha eliminado tu cuenta y todos tus datos correctamente.")
        return redirect('pag_informativa')

    return render(request, 'usuario/confirmar_eliminacion.html')
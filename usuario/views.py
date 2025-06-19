from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from administracion.models import *
from usuario.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from administracion.utils import paginacion_queryset1

@login_required(login_url='/login/')
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

def pagina_informativa(request):
    return render(request, 'usuario/informativo.html')

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
        return redirect('pagina_informativa')

    return render(request, 'usuario/confirmar_eliminacion.html')

@login_required
def agendamiento(request):
    try:

        perfil = request.user.perfilusuario
        
        if not hasattr(request.user, 'perfilusuario') or not hasattr(request.user.perfilusuario, 'usuario_sist'):
            return render(request, 'usuario/agendamiento.html', {
                'sin_atenciones': True,
                'mensaje': 'Tu usuario no tiene un perfil de paciente asignado'
            })
    
        usuario_sist = request.user.perfilusuario.usuario_sist
        if not usuario_sist:
            return render(request, 'usuario/agendamiento.html', {
                'sin_atenciones': True,
                'mensaje': 'No se encontró tu información de paciente'
            })
        
        id_manychat_usuario = usuario_sist.id_manychat
        
        agendamientos_list = Agenda.objects.filter(
            id_manychat=usuario_sist 
        ).select_related(
            'id_cesfam',
            'id_procedimiento'
        ).order_by('-fecha_atencion', '-hora_atencion')
        
        agendamientos = paginacion_queryset1(request, agendamientos_list, items_por_pagina=10)
        
        context = {
            'perfil': perfil,
            'agendamientos': agendamientos,
            'sin_atenciones': not agendamientos_list.exists()
        }
        
        return render(request, 'usuario/agendamiento.html', context)
        
    except ObjectDoesNotExist:
        return render(request, 'usuario/usuario_sin_perfil.html', {
            'mensaje': 'Tu cuenta no tiene un perfil asignado. Contacta con el administrador.'
        }, status=403)
        
    except Exception as e:
        print(f"Error en agendamiento: {str(e)}")
        return render(request, 'usuario/agendamiento.html', {
            'sin_atenciones': True,
            'error': 'Ocurrió un error al cargar tu historial de agendamientos'
        })

@login_required
def visualizar_resp_usuarias (request):
    perfil = get_object_or_404(PerfilUsuario, user=request.user)
    
    if not perfil.usuario_sist:
        return render(request, 'error.html', {'mensaje': 'No tienes cuestionarios completados'})
    
    contexto = {
        # Respuestas TM
        'respuestas_tm': RespTM.objects.filter(
            id_manychat=perfil.usuario_sist
        ).select_related('id_opc_tm__id_preg_tm'),
        
        # Respuestas DS
        'respuestas_ds': RespDS.objects.filter(
            id_manychat=perfil.usuario_sist
        ).select_related('id_opc_ds__id_preg_ds'),
        
        # Respuestas FRM
        'respuestas_frm': RespFRM.objects.filter(
            id_manychat=perfil.usuario_sist
        ).select_related('id_opc_frm__id_preg_frm'),
        
        # Respuestas FRNM
        'respuestas_frnm': RespFRNM.objects.filter(
            id_manychat=perfil.usuario_sist
        ).select_related('id_opc_frnm__id_preg_frnm'),
        
        # Preguntas textuales
        'preguntas_textuales': UsuarioTextoPregunta.objects.filter(
            id_manychat=perfil.usuario_sist
        ),
        
        'perfil': perfil
    }
    
    return render(request, 'usuario/respuestas_usuarias.html', contexto)

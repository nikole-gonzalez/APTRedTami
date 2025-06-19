from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User 
from django.contrib.auth.decorators import login_required
from administracion.models import PerfilUsuario, Usuario
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "¡Bienvenido de nuevo!")

            # Caso 1: superuser o is_staff
            if user.is_superuser or user.is_staff:
                return redirect('admin_index')

            # Caso 2: tiene perfil y es administrador
            if hasattr(user, 'perfilusuario'):
                perfil = user.perfilusuario
                if perfil.tipo_usuario == 'administrador':
                    return redirect('admin_index')
                elif perfil.tipo_usuario == 'paciente':
                    return redirect('usuario_index')

            # Caso 3: no tiene perfil 
            return redirect('pagina_informativa')
        
        else:
            messages.error(request, "Credenciales inválidas")
    
    return render(request, 'registration/login.html')

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')  


def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "¡Registro exitoso!")
                return redirect('usuario_index')
            except forms.ValidationError as e:
                # Añade el error al formulario sin hacer raise
                form.add_error(None, e)
    else:
        initial_data = {}
        if request.GET.get('email'):
            initial_data['email'] = request.GET.get('email')
        form = RegistroForm(initial=initial_data)
    
    return render(request, 'core/registro/registro.html', {
        'form': form,
        'manychat_id': request.GET.get('manychat_id', '')
    })

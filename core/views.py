from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User 
from django.contrib.auth.decorators import login_required
from administracion.models import PerfilUsuario, Usuario
from .forms import RegistroForm
from .utils import verificar_cuestionario_completo
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
            if user.is_staff or user.is_superuser:
                return redirect('admin_index')  
            elif user.groups.filter(name='usuario_cesfam').exists():
                return redirect('cesfam_index')  
            else:
                return redirect('pag_informativa')  
        else:
            messages.error(request, "Credenciales inválidas")
            return render(request, 'registration/login.html')

    
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
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso!")
            return redirect('pag_informativa')
    else:
        initial_data = {}
        if request.GET.get('email'):
            initial_data['email'] = request.GET.get('email')
        form = RegistroForm(initial=initial_data)
    
    return render(request, 'core/registro/registro.html', {
        'form': form,
        'manychat_id': request.GET.get('manychat_id', '')
    })
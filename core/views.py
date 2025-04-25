from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group 
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
                return redirect('usuario_index')  
        else:
            messages.error(request, "Credenciales inválidas")
            return render(request, 'login')

    
    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')  



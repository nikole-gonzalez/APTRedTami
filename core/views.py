from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group  # Importar Group para verificar roles

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirige usando los nombres de URL definidos
            if user.is_staff or user.is_superuser:
                return redirect('admin_index')  
            elif user.groups.filter(name='CESFAM').exists():
                return redirect('cesfam_index')  
            else:
                return redirect('usuario_index')  
        else:
            return render(request, 'registration/login.html', {'error': 'Credenciales inválidas'})
    
    return render(request, 'registration/login.html')
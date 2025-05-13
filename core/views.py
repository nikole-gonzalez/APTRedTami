from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User 
from django.contrib.auth.decorators import login_required
from administracion.models import PerfilUsuario, Usuario
from .forms import RegistroForm
from .utils import verificar_cuestionario_completo
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

def autorregistro_view(request):
    id_manychat = request.GET.get("id")

    if not id_manychat:
        return render(request, "core/error.html", {"mensaje": "No se recibió un ID de usuario válido."})

    try:
        usuario = Usuario.objects.get(pk=id_manychat)
    except Usuario.DoesNotExist:
        return render(request, "core/error.html", {"mensaje": "Usuario no encontrado en base de datos."})

    if not verificar_cuestionario_completo(id_manychat):
        return render(request, "core/error.html", {"mensaje": "No has completado el cuestionario requerido para registrarte."})

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password']
            )
            PerfilUsuario.objects.create(
                user=user,
                telefono=form.cleaned_data['telefono'],
                cod_acceso=form.cleaned_data['cod_acceso'],
                usuario_sist=usuario
            )
            return redirect('panel_usuario')  # Asegúrate de tener esta ruta
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = RegistroForm()

    return render(request, 'core/autorregistro.html', {'form': form, 'nombre_usuario': usuario})


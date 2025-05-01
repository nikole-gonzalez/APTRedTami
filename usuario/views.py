from django.shortcuts import render

def home_usuario(request):
    return render(request, 'usuario/index.html')

def usuario_index(request):
    return render(request, 'usuario/index.html')

def pag_informativa(request):
    return render(request, 'usuario/informativo.html')

def registro_usuario(request):
    return render(request, 'usuario/registro.html')


from django.shortcuts import render

def home_usuario(request):
    return render(request, 'usuario/index.html')




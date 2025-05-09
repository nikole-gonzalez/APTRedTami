from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'email', 'password']
    
class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'cod_acceso', 'usuario_sist']
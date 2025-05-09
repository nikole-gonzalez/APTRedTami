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
        fields = ['telefono', 'cod_acceso', 'usuario_sist', 'tipo_usuario']

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_usuario')
        usuario_sist = cleaned_data.get('usuario_sist')

        if tipo == 'paciente' and not usuario_sist:
            self.add_error('usuario_sist', 'Este campo es obligatorio para pacientes.')
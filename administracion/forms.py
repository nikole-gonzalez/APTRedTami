from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        required=False
    )
    
    class Meta:
        model = User 
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Nombre de Usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'tucorreo@ejemplo.com'
            }),
        }

class PerfilUsuarioForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Número de WhatsApp",
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '912345678'})
    )
    cod_acceso = forms.CharField(
        label="RUT (con guión y dígito verificador)",
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '12345678-9'})
    )
    
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'cod_acceso', 'usuario_sist', 'tipo_usuario']
        widgets = {
            'usuario_sist': forms.Select(attrs={'class': 'input'}),
            'tipo_usuario': forms.Select(attrs={'class': 'input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_usuario')
        usuario_sist = cleaned_data.get('usuario_sist')

        if tipo == 'paciente' and not usuario_sist:
            self.add_error('usuario_sist', 'Este campo es obligatorio para pacientes.')
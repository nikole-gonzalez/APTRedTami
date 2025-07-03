from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Usuario

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

    rut_usuario = forms.IntegerField(
        label="RUT",
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': '12345678'})
    )

    dv_rut = forms.CharField(
        label="Dígito Verificador",
        max_length=1,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'K o número'})
    )

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'rut_usuario', 'dv_rut', 'usuario_sist', 'tipo_usuario']
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

class UsuarioFormParcial(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'num_whatsapp']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo desde ManyChat'}),
            'num_whatsapp': forms.TextInput(attrs={'class': 'input', 'placeholder': '912345678'}),
        }
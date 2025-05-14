from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario
from django.core.validators import RegexValidator
from administracion.models import *

class RegistroForm(UserCreationForm):
    rut = forms.CharField(
        label="RUT (con guión y dígito verificador)",
        required=False,  
        widget=forms.TextInput(attrs={
            'class': 'input', 
            'placeholder': '12345678-9'
        })
    )
    telefono = forms.IntegerField(
        label="Número de WhatsApp",
        validators=[RegexValidator(r'^\d{9,12}$', 'Ingrese un número válido')],
        widget=forms.NumberInput(attrs={
            'class': 'input', 
            'placeholder': '912345678',
            'type': 'tel',
            'inputmode': 'numeric'  
        })
    )
    nombre_completo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input', 
            'placeholder': 'Nombre Completo'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input', 
            'placeholder': 'tucorreo@ejemplo.com'
        })
    )
    
    class Meta:
        model = User 
        fields = ("username", "nombre_completo", "email", "rut", "telefono", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input', 
                'placeholder': 'Nombre de Usuario'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'input', 
                'placeholder': 'Contraseña',
                'autocomplete': 'new-password'

            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'input', 
                'placeholder': 'Confirmar Contraseña',
                'autocomplete': 'new-password'
            }),
        }
    
def clean_email(self):
    email = self.cleaned_data.get('email')
    # Verifica si el email existe en el modelo Usuario (no en User)
    if not Usuario.objects.filter(email=email).exists():
        raise forms.ValidationError("Este correo electrónico no está registrado en nuestro sistema. Completa el cuestionario en ManyChat primero.")
    return email

def clean_telefono(self):
    telefono = self.cleaned_data.get('telefono')
    # Verifica si el teléfono existe en el modelo Usuario
    if not Usuario.objects.filter(num_whatsapp=telefono).exists():
        raise forms.ValidationError("Este número de WhatsApp no está registrado en nuestro sistema. Completa el cuestionario en ManyChat primero.")
    return telefono

def save(self, commit=True):
    # Obtiene el usuario de ManyChat (modelo Usuario)
    email = self.cleaned_data['email']
    telefono = self.cleaned_data['telefono']
    
    try:
        usuario_manychat = Usuario.objects.get(email=email, num_whatsapp=telefono)
    except Usuario.DoesNotExist:
        raise forms.ValidationError("Los datos no coinciden con nuestros registros. Completa el cuestionario en ManyChat primero.")
    
    # Crea el usuario Django
    user = super().save(commit=False)
    user.email = email
    if commit:
        user.save()
    
    # Crea el perfil vinculando al usuario de ManyChat
    PerfilUsuario.objects.create(
        user=user,
        usuario_sist=usuario_manychat,  # Vinculación directa
        telefono=telefono,
        cod_acceso=self.cleaned_data['rut'],
        tipo_usuario='paciente'
    )
    
    return user
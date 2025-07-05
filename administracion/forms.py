from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Usuario
from django.core.validators import RegexValidator
from core.validators import validar_rut_chileno

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'Nueva contraseña'
        }),
        required=False,
        help_text="Dejar en blanco para mantener la contraseña actual"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=False,
        label="Confirmar Contraseña"
    )
    
    class Meta:
        model = User 
        fields = ['username', 'first_name', 'last_name', 'email']
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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden.')

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class PerfilUsuarioForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Número de WhatsApp",
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': '912345678',
            'pattern': r'^[9]\d{8}$',
            'title': 'Ingrese número chileno empezando con 9 (911111111)'
        }),
        required=False,
        help_text="Obligatorio para pacientes. Formato: 911111111"
    )

    rut_usuario = forms.IntegerField(
        label="RUT (sin puntos ni guión)",
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': '12345678',
            'min': '1000000',
            'max': '99999999'
        })
    )

    dv_rut = forms.CharField(
        label="Dígito Verificador",
        max_length=1,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'K o número',
            'pattern': r'[\dKk]',
            'title': 'Ingrese dígito verificador (0-9 o K)'
        })
    )

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'rut_usuario', 'dv_rut', 'usuario_sist', 'tipo_usuario']
        widgets = {
            'usuario_sist': forms.Select(attrs={
                'class': 'input',
            }),
            'tipo_usuario': forms.Select(attrs={
                'class': 'input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.tipo_usuario == 'administrador':
            self.fields['usuario_sist'].required = False
            self.fields['telefono'].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_usuario')
        usuario_sist = cleaned_data.get('usuario_sist')
        telefono = cleaned_data.get('telefono')
        rut = cleaned_data.get('rut_usuario')
        dv = cleaned_data.get('dv_rut', '').upper()

        if tipo == 'paciente':
            if not usuario_sist:
                self.add_error('usuario_sist', 'Este campo es obligatorio para pacientes.')
            if not telefono:
                self.add_error('telefono', 'Este campo es obligatorio para pacientes.')
            elif not telefono.startswith('9') or len(telefono) != 9:
                self.add_error('telefono', 'Ingrese un número chileno válido (911111111)')

        else:
            cleaned_data['usuario_sist'] = None

        if rut and dv:
            rut_completo = f"{rut}-{dv}"
            if not validar_rut_chileno(rut_completo):
                self.add_error('dv_rut', 'El RUT no es válido. Verifique el número y dígito verificador.')

        return cleaned_data

class UsuarioFormParcial(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'num_whatsapp']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo desde ManyChat'}),
            'num_whatsapp': forms.TextInput(attrs={'class': 'input', 'placeholder': '912345678'}),
        }
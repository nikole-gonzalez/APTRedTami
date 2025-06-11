from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Usuario
from django.core.validators import RegexValidator


class RegistroForm(UserCreationForm):
    rut = forms.CharField(
        label="RUT (con guión y dígito verificador)",
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '12345678-9'})
    )
    telefono = forms.IntegerField(
        label="Número de WhatsApp",
        validators=[RegexValidator(r'^\d{9,12}$', 'Ingrese un número válido')],
        widget=forms.NumberInput(attrs={'class': 'input', 'placeholder': '912345678'})
    )

    telefono = forms.IntegerField(
        label="Número de WhatsApp",
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': '912345678',
            'min': '900000000',
            'max': '999999999'
        }),
        help_text="Ingresa tu número de WhatsApp empezando con 9 (ej: 912345678)"
    )

    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Apellido'})

    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'tucorreo@ejemplo.com'})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name","email", "rut", "telefono", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de Usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirmar Contraseña'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico no está registrado en nuestro sistema.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está siendo utilizado. Por favor, inicia sesión o usa otro.")
        return email

    def clean_telefono(self):
        telefono = str(self.cleaned_data.get('telefono'))
        
        if not telefono.startswith('9') or len(telefono) != 9:
            raise forms.ValidationError("Debe ser un número de 9 dígitos que empiece con 9")
        
        try:
            telefono_completo = int('56' + telefono)
        except (ValueError, TypeError):
            raise forms.ValidationError("Número inválido")
        
        if not Usuario.objects.filter(num_whatsapp=telefono_completo).exists():
            raise forms.ValidationError("Número no registrado en el sistema")
        
        return telefono_completo

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut or '-' not in rut:
            raise forms.ValidationError("El RUT debe incluir guión y dígito verificador.")
        rut_sin_dv, dv = rut.split('-')
        if not Usuario.objects.filter(rut_usuario=rut_sin_dv, dv_rut=dv).exists():
            raise forms.ValidationError("El RUT no se encuentra registrado en el sistema.")
        return rut
    
    def save(self, commit=True):
        email = self.cleaned_data['email']
        telefono = self.cleaned_data['telefono']
        rut = self.cleaned_data['rut']
        rut_sin_dv, dv = rut.split('-')

        try:
            usuario_manychat = Usuario.objects.get(
                email=email,
                num_whatsapp=telefono,
                rut_usuario=rut_sin_dv,
                dv_rut=dv
            )
            
            # Verificar si ya existe un perfil para este usuario
            if PerfilUsuario.objects.filter(usuario_sist=usuario_manychat).exists():
                raise forms.ValidationError(
                    "Ya existe una cuenta asociada a estos datos. Por favor inicia sesión.",
                    code='cuenta_existente'
                )

            if not usuario_manychat.cuestionario_completo():
                raise forms.ValidationError(
                    "Debes completar todos los cuestionarios en ManyChat antes de registrarte.",
                    code='cuestionario_incompleto'
                )

            user = super().save(commit=False)
            user.email = email
            if commit:
                user.save()

            PerfilUsuario.objects.create(
                user=user,
                usuario_sist=usuario_manychat,
                telefono=telefono,
                cod_acceso=rut,
                tipo_usuario='paciente'
            )

            return user

        except Usuario.DoesNotExist:
            raise forms.ValidationError(
                "Los datos no coinciden con nuestros registros.",
                code='datos_no_coinciden'
            )
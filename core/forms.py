from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Usuario
from django.core.validators import RegexValidator
from administracion.utils import encrypt_data, decrypt_data

class RegistroForm(UserCreationForm):
    rut = forms.CharField(
        label="RUT (con guión y dígito verificador)",
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '12345678-9'})
    )

    telefono = forms.IntegerField(
        label="Número de WhatsApp",
        validators=[RegexValidator(r'^\d{9}$', 'Ingrese un número válido de 9 dígitos')],
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
        fields = ("username", "first_name", "last_name", "email", "rut", "telefono", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de Usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Confirmar Contraseña'}),
        }

    def clean_telefono(self):
        telefono = str(self.cleaned_data.get('telefono'))

        if not telefono.startswith('9') or len(telefono) != 9:
            raise forms.ValidationError("Debe ser un número de 9 dígitos que empiece con 9")

        telefono_completo = '56' + telefono  # Formato: 569XXXXXXXX

        usuarios = Usuario.objects.all()
        for usuario in usuarios:
            whatsapp_descifrado = usuario.get_whatsapp_descifrado()
            if whatsapp_descifrado and whatsapp_descifrado.strip() == telefono_completo:
                return telefono_completo  # 👈 Como string

        raise forms.ValidationError("Número no registrado en el sistema")

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut or '-' not in rut:
            raise forms.ValidationError("El RUT debe incluir guión y dígito verificador.")

        rut_sin_dv, dv = rut.split('-')

        if not rut_sin_dv.isdigit() or len(dv) != 1:
            raise forms.ValidationError("Formato de RUT inválido")

        usuarios = Usuario.objects.all()
        for usuario in usuarios:
            rut_descifrado = usuario.get_rut_descifrado()
            dv_descifrado = usuario.get_dv_descifrado()
            if rut_descifrado == rut_sin_dv and dv_descifrado == dv:
                return rut

        raise forms.ValidationError("El RUT no se encuentra registrado en el sistema.")

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()

        if not email:
            raise forms.ValidationError("El correo electrónico es requerido")

        usuarios = Usuario.objects.all()
        for usuario in usuarios:
            email_descifrado = usuario.get_email_descifrado()
            if email_descifrado and email_descifrado.lower() == email:
                if User.objects.filter(email__iexact=email).exists():
                    raise forms.ValidationError("Este correo ya está siendo utilizado. Por favor, inicia sesión o usa otro.")
                return email

        raise forms.ValidationError("Este correo electrónico no está registrado en nuestro sistema.")

    def save(self, commit=True):
        email = self.cleaned_data['email']
        telefono = self.cleaned_data['telefono']  # Ya es el formato '569XXXXXXXX' como string
        rut = self.cleaned_data['rut']
        rut_sin_dv, dv = rut.split('-')

        usuarios = Usuario.objects.all()
        usuario_manychat = None

        for usuario in usuarios:
            email_descifrado = usuario.get_email_descifrado()
            whatsapp_descifrado = usuario.get_whatsapp_descifrado()
            rut_descifrado = usuario.get_rut_descifrado()
            dv_descifrado = usuario.get_dv_descifrado()

            if (
                email_descifrado and email_descifrado.lower() == email.lower() and
                whatsapp_descifrado and whatsapp_descifrado.strip() == str(telefono).strip() and
                rut_descifrado == rut_sin_dv and
                dv_descifrado == dv
            ):
                usuario_manychat = usuario
                break

        if not usuario_manychat:
            raise forms.ValidationError("Los datos no coinciden con nuestros registros.")

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
            rut_usuario=rut_sin_dv,
            dv_rut=dv,
            tipo_usuario='paciente'
        )

        return user

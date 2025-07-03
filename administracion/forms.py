from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Usuario
from django.core.exceptions import ValidationError

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
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': '912345678',
            'pattern': '[0-9]{9}',
            'title': 'Ingrese un número de 9 dígitos sin espacios ni símbolos'
        }),
        required=False,
        help_text="Formato: 9 dígitos (ej: 912345678)"
    )

    rut_usuario = forms.IntegerField(
        label="RUT (sin puntos ni guión)",
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': '12345678',
            'min': '1000000',
            'max': '99999999'
        }),
        required=False,
        help_text="Solo números (ej: 12345678)"
    )

    dv_rut = forms.CharField(
        label="Dígito Verificador",
        max_length=1,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'K o número',
            'pattern': '[0-9kK]',
            'title': 'Ingrese un dígito (0-9) o la letra K'
        }),
        required=False,
        help_text="Un dígito (0-9) o la letra K"
    )

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'rut_usuario', 'dv_rut', 'usuario_sist', 'tipo_usuario']
        widgets = {
            'usuario_sist': forms.Select(attrs={'class': 'input'}),
            'tipo_usuario': forms.Select(attrs={
                'class': 'input',
                'onchange': 'toggleUsuarioSistField(this)'
            }),
        }
        labels = {
            'usuario_sist': 'Usuario asociado en ManyChat',
            'tipo_usuario': 'Tipo de Usuario'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance and instance.pk:
            # Mostrar datos descifrados en el formulario
            self.fields['telefono'].initial = instance.get_telefono_descifrado()
            self.fields['rut_usuario'].initial = instance.get_rut_descifrado()
            self.fields['dv_rut'].initial = instance.get_dv_descifrado()
            
            # Configurar campo usuario_sist según tipo_usuario
            if instance.tipo_usuario == 'administrador':
                self.fields['usuario_sist'].required = False
                self.fields['usuario_sist'].widget.attrs['disabled'] = True
            else:
                self.fields['usuario_sist'].required = True

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Validar formato del teléfono
            if not telefono.isdigit() or len(telefono) != 9:
                raise ValidationError("El teléfono debe tener 9 dígitos numéricos")
        return telefono

    def clean_rut_usuario(self):
        rut = self.cleaned_data.get('rut_usuario')
        if rut:
            # Validar rango del RUT
            if rut < 1000000 or rut > 99999999:
                raise ValidationError("El RUT debe estar entre 1.000.000 y 99.999.999")
        return rut

    def clean_dv_rut(self):
        dv = self.cleaned_data.get('dv_rut', '').upper()
        if dv:
            # Validar formato del DV
            if not (dv.isdigit() or dv == 'K'):
                raise ValidationError("El dígito verificador debe ser un número (0-9) o la letra K")
        return dv

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        usuario_sist = cleaned_data.get('usuario_sist')

        # Validar que si es paciente, tenga usuario_sist
        if tipo_usuario == 'paciente' and not usuario_sist:
            self.add_error('usuario_sist', 'Este campo es obligatorio para pacientes')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar valores sin cifrar (el cifrado se hará en el save() del modelo)
        if 'telefono' in self.cleaned_data:
            instance.telefono = self.cleaned_data['telefono'] or None
            
        if 'rut_usuario' in self.cleaned_data:
            instance.rut_usuario = str(self.cleaned_data['rut_usuario']) if self.cleaned_data['rut_usuario'] else None
            
        if 'dv_rut' in self.cleaned_data:
            instance.dv_rut = self.cleaned_data['dv_rut'] or None
        
        if commit:
            instance.save()
        return instance

    

class UsuarioFormParcial(forms.ModelForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo desde ManyChat'}),
        required=False
    )
    num_whatsapp = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': '912345678'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['email', 'num_whatsapp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.get_email_descifrado()
            self.fields['num_whatsapp'].initial = self.instance.get_whatsapp_descifrado()

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Los datos se cifrarán en la view antes de guardar
        if 'email' in self.cleaned_data:
            instance.email = self.cleaned_data['email']
        if 'num_whatsapp' in self.cleaned_data:
            instance.num_whatsapp = self.cleaned_data['num_whatsapp']
        
        if commit:
            instance.save()
        return instance
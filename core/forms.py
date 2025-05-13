# core/forms.py
from django import forms
from django.contrib.auth.models import User
from administracion.models import PerfilUsuario

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    telefono = forms.IntegerField()
    cod_acceso = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirmar_password")
        if password != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

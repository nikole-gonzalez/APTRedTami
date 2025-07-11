from rest_framework import serializers
from administracion.models import (
    Usuario, PerfilUsuario, Comuna, Region, Provincia,
    UsuarioTextoPregunta, RespFRM, RespFRNM, RespDS,
    PregFRM, OpcFRM, PregFRNM, OpcFRNM, PregDS, OpcDS,
    PregTM, OpcTM, RespTM, Divulgacion
)
from datetime import datetime
from fuzzywuzzy import fuzz
from unidecode import unidecode
import re 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UsuarioSerializer(serializers.ModelSerializer):

    rut_completo = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {
            'rut_usuario': {'read_only': True},
            'dv_rut': {'read_only': True},
        }

    def to_internal_value(self, data):
        # Manejo de fecha en texto natural
        fecha = data.get('fecha_nacimiento')
        if isinstance(fecha, str):
            meses_correctos = [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
            ]
            fecha_normalizada = unidecode(fecha.lower())
            for mes in meses_correctos:
                for palabra in fecha_normalizada.split():
                    if fuzz.ratio(palabra, mes) > 70:
                        fecha_normalizada = fecha_normalizada.replace(palabra, mes)

            formatos_fecha = [
                "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d de %B de %Y",
                "%d/%m/%y", "%d-%m-%y", "%d de %B del %Y", "%d de %B del %y"
            ]
            for formato in formatos_fecha:
                try:
                    data['fecha_nacimiento'] = datetime.strptime(fecha_normalizada, formato)
                    break
                except ValueError:
                    continue
            else:
                raise serializers.ValidationError({
                    "fecha_nacimiento": f"Formato inválido: '{fecha}'. Usa dd/mm/yyyy o '12 de mayo del 2000'."
                })

        return super().to_internal_value(data)

    def create(self, validated_data):
        rut_completo = validated_data.pop("rut_completo", None)
        if rut_completo:
            rut_completo = rut_completo.replace(".", "").replace("-", "").upper()
            validated_data["rut_usuario"] = int(rut_completo[:-1])
            validated_data["dv_rut"] = rut_completo[-1]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        rut_completo = validated_data.pop("rut_completo", None)
        if rut_completo:
            rut_completo = rut_completo.replace(".", "").replace("-", "").upper()
            validated_data["rut_usuario"] = int(rut_completo[:-1])
            validated_data["dv_rut"] = rut_completo[-1]
        return super().update(instance, validated_data)

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = "__all__"


class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = "__all__"


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = "__all__"

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"

class UsuarioTextoPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioTextoPregunta
        fields = "__all__"


class UsuarioRespuestaFRMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespFRM
        fields = "__all__"


class UsuarioRespuestaFRNMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespFRNM
        fields = "__all__"


class UsuarioRespuestaDSSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespDS
        fields = "__all__"

class UsuarioRespuestaTMSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespTM
        fields = "__all__"

class PreguntaFRMSerializer(serializers.ModelSerializer):
    class Meta:
        model = PregFRM
        fields = "__all__"


class OpcionFRMSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcFRM
        fields = "__all__"


class PreguntaFRNMSerializer(serializers.ModelSerializer):
    class Meta:
        model = PregFRNM
        fields = "__all__"


class OpcionFRNMSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcFRNM
        fields = "__all__"


class PreguntaDSSerializer(serializers.ModelSerializer):
    class Meta:
        model = PregDS
        fields = "__all__"


class OpcionDSSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcDS
        fields = "__all__"


class PreguntaTMSerializer(serializers.ModelSerializer):
    class Meta:
        model = PregTM
        fields = "__all__"


class OpcionTMSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcTM
        fields = "__all__"


class DivulgacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Divulgacion
        fields = "__all__"
        
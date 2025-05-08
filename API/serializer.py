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

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {
            'rut_usuario': {'read_only': True},
            'dv_rut': {'read_only': True},
        }
    
    def get_rut_completo_display(self, obj):
        return f"{obj.rut_usuario}{obj.dv_rut}"

    def validate_rut_completo(self, value):
        value = value.replace(".", "").replace("-", "").upper()
        if not re.match(r"^\d{7,8}[0-9K]$", value):
            raise serializers.ValidationError("Formato de RUT inválido. Debe ser 12345678K.")
        
        rut = int(value[:-1])
        dv = value[-1]

        if not self.validar_dv(rut, dv):
            raise serializers.ValidationError("Dígito verificador incorrecto para el RUT ingresado.")
        
        return value
    
    def to_internal_value(self, data):
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
                    "fecha_nacimiento": f"Formato inválido: '{fecha}'. Usa dd/mm/yyyy o '12 de mayo del 2000'"
                })

        return super().to_internal_value(data)

    def create(self, validated_data):
        rut_completo = validated_data.pop("rut_completo")
        rut = int(rut_completo[:-1])
        dv = rut_completo[-1].upper()
        validated_data["rut_usuario"] = rut
        validated_data["dv_rut"] = dv
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "rut_completo" in validated_data:
            rut_completo = validated_data.pop("rut_completo")
            rut = int(rut_completo[:-1])
            dv = rut_completo[-1].upper()
            validated_data["rut_usuario"] = rut
            validated_data["dv_rut"] = dv
        return super().update(instance, validated_data)

    def validar_dv(self, rut, dv):
        suma = 0
        multiplo = 2
        while rut > 0:
            suma += (rut % 10) * multiplo
            rut = rut // 10
            multiplo = 2 if multiplo == 7 else multiplo + 1
        resto = suma % 11
        dv_esperado = 'K' if (11 - resto) == 10 else '0' if (11 - resto) == 11 else str(11 - resto)
        return dv == dv_esperado


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



# ------------ SERIALIZER USUARIOS -------------# 

''' from rest_framework import serializers
from .models import Agenda, Cesfam, TipoProcedimiento, CodigoFonasa, CodigoSnomed
from administracion.models import Usuario, Comuna

class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = '__all__'

class UsuarioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'RutHash']  # Ajusta los campos necesarios

class CesfamSerializer(serializers.ModelSerializer):
    cod_comuna = ComunaSerializer(read_only=True)

    class Meta:
        model = Cesfam
        fields = '__all__'

class CodigoFonasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoFonasa
        fields = '__all__'

class CodigoSnomedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoSnomed
        fields = '__all__'

class TipoProcedimientoSerializer(serializers.ModelSerializer):
    cod_snomed = CodigoSnomedSerializer(read_only=True)
    cod_fonasa = CodigoFonasaSerializer(read_only=True)

    class Meta:
        model = TipoProcedimiento
        fields = '__all__'

class AgendaSerializer(serializers.ModelSerializer):
    id_cesfam = CesfamSerializer(read_only=True)
    id_usuario = UsuarioSimpleSerializer(read_only=True)
    id_procedimiento = TipoProcedimientoSerializer(read_only=True)

    class Meta:
        model = Agenda
        fields = '__all__'  '''

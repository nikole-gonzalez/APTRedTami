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

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"

    def validate_fecha_nacimiento(self, value):
        if value:
            meses_correctos = [
                "enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
            ]
            fecha_normalizada = unidecode(value.lower())
            for mes in meses_correctos:
                palabras_fecha = fecha_normalizada.split()
                for palabra in palabras_fecha:
                    puntaje = fuzz.ratio(palabra, mes)
                    if puntaje > 70:
                        fecha_normalizada = fecha_normalizada.replace(palabra, mes)

            formatos_fecha = [
                "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d de %B de %Y", "%d %m %Y",
                "%d/%m/%y", "%d-%m-%y", "%d %m %y", "%d de %B del %Y", "%d de %B del %y",
                "%d de %B %y", "%d de %B %Y", "%d de %b %Y", "%d de %b %y",
                "%d de %b del %Y", "%d de %b del %y"
            ]
            for formato in formatos_fecha:
                try:
                    return datetime.strptime(fecha_normalizada, formato).date()
                except ValueError:
                    continue
            raise serializers.ValidationError(
                f"Formato de fecha inválido. Recibido: '{value}'. Usa dd/mm/yyyy, dd-mm-yyyy, o 'día de mes de año'."
            )
        return value


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

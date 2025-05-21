from django.shortcuts import render
from usuario.models import HoraAgenda, Agenda, TipoProcedimiento
from administracion.models import Usuario
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.db import connection, transaction
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
import requests
import logging
import hashlib

from .models import *
from .serializer import *

def home_api(request):
    return render(request, 'api/index.html')

# Página principal protegida
@login_required
def apiHome(request):
    return render(request, "api/apiHome.html")

# ------------------ ViewSets (CRUD para admin) ------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class TMViewSet(viewsets.ModelViewSet):
    queryset = RespTM.objects.all()
    serializer_class = UsuarioRespuestaTMSerializer

class UsuarioTextoPreguntaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioTextoPregunta.objects.all()
    serializer_class = UsuarioTextoPreguntaSerializer

class FRNMViewSet(viewsets.ModelViewSet):
    queryset = RespFRNM.objects.all()
    serializer_class = UsuarioRespuestaFRNMSerializer

class FRMViewSet(viewsets.ModelViewSet):
    queryset = RespFRM.objects.all()
    serializer_class = UsuarioRespuestaFRMSerializer

class DSViewSet(viewsets.ModelViewSet):
    queryset = RespDS.objects.all()
    serializer_class = UsuarioRespuestaDSSerializer

class DivulgacionViewSet(viewsets.ModelViewSet):
    queryset = Divulgacion.objects.all()
    serializer_class = DivulgacionSerializer

# ------------------ APIViews ------------------

class BaseAdminAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

class UsuarioAPIView(BaseAdminAPIView):
    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

class UsuarioRespuestaTMAPIView(BaseAdminAPIView):
    def get(self, request):
        respuestas = RespTM.objects.all()
        serializer = UsuarioRespuestaTMSerializer(respuestas, many=True)
        return Response(serializer.data)

class UsuarioTextoPreguntaAPIView(BaseAdminAPIView):
    def get(self, request):
        preguntas = UsuarioTextoPregunta.objects.all()
        serializer = UsuarioTextoPreguntaSerializer(preguntas, many=True)
        return Response(serializer.data)

class UsuarioRespuestFRNMaAPIView(BaseAdminAPIView):
    def get(self, request):
        respuestas = RespFRNM.objects.all()
        serializer = UsuarioRespuestaFRNMSerializer(respuestas, many=True)
        return Response(serializer.data)

class UsuarioRespuestFRMaAPIView(BaseAdminAPIView):
    def get(self, request):
        respuestas = RespFRM.objects.all()
        serializer = UsuarioRespuestaFRMSerializer(respuestas, many=True)
        return Response(serializer.data)
    
class DivulgacionAPIView(BaseAdminAPIView):
    def get(self, request):
        respuestas = Divulgacion.objects.all()
        serializer = DivulgacionSerializer(respuestas, many = True)
        return Response(serializer.data)

# ------------------ API Custom ------------------

def generar_hash(valor):
    return hashlib.sha256(valor.encode()).hexdigest()

class ObtenerID(APIView):
    def get(self, request):
        hoy = date.today()
        registro = Divulgacion.objects.filter(fecha=hoy).first()
        if registro:
            return Response({'id': registro.id, 'texto': registro.texto, 'genero': registro.Genero_Usuario.OPC_Genero})
        return Response({'error_code': '1'})

@csrf_exempt
def obtener_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        fecha_formateada = usuario.fecha_nacimiento.strftime("%d/%m/%Y") if usuario.fecha_nacimiento else None
        return JsonResponse({
            "id_manychat": usuario.id_manychat,
            "fecha_nacimiento": usuario.fecha_nacimiento,
            "AnioNacimiento": fecha_formateada
        })
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

@csrf_exempt
def consultar_estado_pregunta(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    try:
        data = JSONParser().parse(request)
    except Exception:
        return JsonResponse({"error": "Error al leer el JSON."}, status=400)

    rut = data.get("Rut")
    tipo = data.get("tipo_pregunta")
    nombre_pregunta = data.get("nombre_pregunta")

    if not rut or not tipo or not nombre_pregunta:
        return JsonResponse({"error": "Campos obligatorios faltantes."}, status=400)

    rut_hash = generar_hash(rut)
    usuario = Usuario.objects.filter(RutHash=rut_hash).first()

    if not usuario:
        return JsonResponse({"respondido": "false"})

    respondido = False

    if tipo == "TM":
        pregunta = PregTM.objects.filter(pregunta=nombre_pregunta).first()
        if pregunta:
            opciones = OpcTM.objects.filter(id_pregunta=pregunta.id)
            respondido = RespTM.objects.filter(RutHash=rut_hash, id_opc_respuesta__in=opciones).exists()

    elif tipo == "DS":
        pregunta = PregDS.objects.filter(pregunta_DS=nombre_pregunta).first()
        if pregunta:
            opciones = OpcDS.objects.filter(id_pregunta_DS=pregunta.id)
            respondido = RespDS.objects.filter(RutHash=rut_hash, respuesta_DS__in=opciones).exists()

    elif tipo == "FRM":
        pregunta = PregFRM.objects.filter(pregunta_FRM=nombre_pregunta).first()
        if pregunta:
            opciones = OpcFRM.objects.filter(id_pregunta_FRM=pregunta.id)
            respondido = RespFRM.objects.filter(RutHash=rut_hash, respuesta_FRM__in=opciones).exists()

    elif tipo == "FRNM":
        pregunta = PregFRNM.objects.filter(pregunta_FRNM=nombre_pregunta).first()
        if pregunta:
            opciones = OpcFRNM.objects.filter(id_pregunta_FRNM=pregunta.id)
            respondido = RespFRNM.objects.filter(RutHash=rut_hash, respuesta_FRNM__in=opciones).exists()

    return JsonResponse({"respondido": "true" if respondido else "false"})

@csrf_exempt
def retorna_genero(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    try:
        data = JSONParser().parse(request)
    except Exception:
        return JsonResponse({"error": "Error al leer el JSON."}, status=400)

    rut = data.get("Rut")
    if not rut:
        return JsonResponse({"error": "El campo 'Rut' es obligatorio."}, status=400)

    rut_hash = generar_hash(rut)
    usuario = Usuario.objects.filter(RutHash=rut_hash).first()

    if not usuario:
        return JsonResponse({"error": "usuario no existe"})

    pregunta = PregFRNM.objects.filter(pregunta_FRNM="¿Cuál es tu género?").first()
    if pregunta:
        opciones = OpcFRNM.objects.filter(id_pregunta_FRNM=pregunta.id)
        respuesta = RespFRNM.objects.filter(RutHash=rut_hash, respuesta_FRNM__in=opciones).first()
        if respuesta:
            return JsonResponse({"genero": respuesta.id_opc_frnm.id})
    
    return JsonResponse({"error": "respuesta no encontrada"})

@csrf_exempt
def verificar_usuario(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    try:
        data = JSONParser().parse(request)
    except Exception:
        return JsonResponse({"error": "Error al leer el JSON."}, status=400)

    rut = data.get("Rut")
    if not rut:
        return JsonResponse({"error": "El campo 'Rut' es obligatorio."}, status=400)

    rut_hash = generar_hash(rut)
    existe = Usuario.objects.filter(RutHash=rut_hash).exists()
    return JsonResponse({"existe": "true" if existe else "false"})

@api_view(['POST'])
@permission_classes([AllowAny])
def cuestionario_completo(request):
    if not request.data or 'id_manychat' not in request.data:
        return Response(
            {'error': 'El campo id_manychat es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    id_manychat = request.data['id_manychat']

    try:
        usuario = Usuario.objects.get(id_manychat=id_manychat)
        
        # Verificar cada tipo de pregunta
        tipos = ['TM', 'DS', 'FRM', 'FRNM']
        completo = True
        
        for tipo in tipos:
            if not verificar_tipo_completo(usuario, tipo):
                completo = False
                break

        return Response({'completo': completo})

    except ObjectDoesNotExist:
        return Response(
            {'completo': False, 'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

def verificar_tipo_completo(usuario, tipo):
    """Verifica si un usuario respondió todas las preguntas de un tipo específico"""
    if tipo == 'TM':
        total_preguntas = PregTM.objects.count()
        respuestas_count = RespTM.objects.filter(id_manychat=usuario).values('id_opc_tm__id_preg_tm').distinct().count()
    elif tipo == 'DS':
        total_preguntas = PregDS.objects.count()
        respuestas_count = RespDS.objects.filter(id_manychat=usuario).values('id_opc_ds__id_preg_ds').distinct().count()
    elif tipo == 'FRM':
        total_preguntas = PregFRM.objects.count()
        respuestas_count = RespFRM.objects.filter(id_manychat=usuario).values('id_opc_frm__id_preg_frm').distinct().count()
    elif tipo == 'FRNM':
        total_preguntas = PregFRNM.objects.count()
        respuestas_count = RespFRNM.objects.filter(id_manychat=usuario).values('id_opc_frnm__id_preg_frnm').distinct().count()
    else:
        return False

    return total_preguntas > 0 and respuestas_count == total_preguntas

logger = logging.getLogger(__name__)


FERIADOS_FIJOS = [
    "01-01",  
    "01-05",
    "21-05",
    "20-06",
    "29-06",
    "16-07",
    "15-08",
    "18-09",  
    "19-09",  
    "25-12",  
]

def es_feriado(fecha):
    """
    Verifica si una fecha es feriado en Chile
    """
    # Verificar feriados fijos
    if fecha.strftime("%d-%m") in FERIADOS_FIJOS:
        return True
    
    # Opcional: Consultar API de feriados (recomendado para feriados variables)
    try:
        año = fecha.year
        response = requests.get(f'https://api.victorsanmartin.com/feriados/en/{año}')
        if response.status_code == 200:
            feriados = response.json()
            return any(f['date'] == fecha.strftime("%Y-%m-%d") for f in feriados)
    except Exception as e:
        logger.error(f"Error al consultar API de feriados: {str(e)}")
    
    return False

def obtener_dia_habil_siguiente(fecha):
    """
    Obtiene el siguiente día hábil (no fin de semana ni feriado)
    """
    dias_saltados = 0
    while True:
        nueva_fecha = fecha + timedelta(days=1)
        # Saltar fines de semana (5=sábado, 6=domingo)
        if nueva_fecha.weekday() >= 5:
            fecha = nueva_fecha
            continue
        # Saltar feriados
        if es_feriado(nueva_fecha):
            fecha = nueva_fecha
            continue
        return nueva_fecha

@api_view(['POST'])
def horas_disponibles(request):
    try:
        data = request.data
        cesfam_id = data.get('cesfam_id')
        
        if not cesfam_id:
            return Response(
                {'error': 'Se requiere cesfam_id'}, 
                status=400
            )
        
        # Obtener fecha actual
        hoy = datetime.now().date()
        fecha_busqueda = hoy
        
        # Lista para acumular resultados
        horas_disponibles = []
        dias_buscados = 0
        max_dias_busqueda = 14  # Límite para evitar bucles infinitos
        
        while len(horas_disponibles) < 3 and dias_buscados < max_dias_busqueda:
            # Si es fin de semana o feriado, saltar al siguiente día hábil
            if fecha_busqueda.weekday() >= 5 or es_feriado(fecha_busqueda):
                fecha_busqueda = obtener_dia_habil_siguiente(fecha_busqueda)
                dias_buscados += 1
                continue
            
            # Buscar horas disponibles para este día
            horas_del_dia = HoraAgenda.objects.filter(
                fecha=fecha_busqueda,
                estado='disponible',
                cesfam_id=cesfam_id
            ).order_by('hora')
            
            # Agregar a los resultados
            for hora in horas_del_dia:
                if len(horas_disponibles) >= 3:
                    break
                    
                horas_disponibles.append({
                    'hora_id': str(hora.id_hora), 
                    'display_text': f"{hora.fecha.strftime('%d/%m/%Y')} {hora.hora.strftime('%H:%M')}",
                    'fecha': hora.fecha.strftime('%d/%m/%Y'),
                    'hora': hora.hora.strftime('%H:%M'),
                    'dia': 'Hoy' if hora.fecha == hoy else 'Próximos días'
                })
            
            # Pasar al siguiente día
            fecha_busqueda += timedelta(days=1)
            dias_buscados += 1
        
        return Response({
            'horas_disponibles': horas_disponibles[:3],  # Aseguramos máximo 3
            'fecha_consulta': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'cache': False
        })
        
    except Exception as e:
        logger.error(f"Error en horas_disponibles: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Error al obtener horas disponibles'}, 
            status=500
        )
logger = logging.getLogger(__name__)

import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)

from django.db import transaction, connection, DatabaseError
from django.utils import timezone
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Agenda, Usuario
import logging

# Configuración de logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@transaction.atomic
def reservar_hora(request):
    try:
        # 1. Obtener y validar datos básicos
        data = request.data
        hora_id = data.get('hora_id')
        manychat_id = data.get('manychat_id')
        requisito_examen = data.get('requisito_examen', '')
        procedimiento_id = data.get('procedimiento_id')

        # Validación de campos requeridos
        if not all([hora_id, manychat_id, procedimiento_id]):
            logger.warning('Faltan campos requeridos en la solicitud')
            return Response(
                {
                    'success': "false",
                    'error': 'Datos incompletos',
                    'detalle': 'Se requieren hora_id, manychat_id y procedimiento_id',
                    'codigo_error': 'DATOS_INCOMPLETOS'
                },
                status=400
            )

        # 2. Validar formato de IDs
        try:
            hora_id = int(hora_id)
            procedimiento_id = int(procedimiento_id)
        except (ValueError, TypeError):
            logger.error('IDs con formato inválido')
            return Response(
                {
                    'success': "false",
                    'error': 'IDs inválidos',
                    'detalle': 'hora_id y procedimiento_id deben ser números',
                    'codigo_error': 'ID_INVALIDO'
                },
                status=400
            )

        # 3. Verificar existencia y disponibilidad de la hora
        with connection.cursor() as cursor:
            try:
                # Verificar si la hora existe
                cursor.execute("""
                    SELECT estado, fecha, hora, id_cesfam 
                    FROM usuario_horas_agenda 
                    WHERE id_hora = %s
                    FOR UPDATE
                """, [hora_id])
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f'Hora no encontrada: {hora_id}')
                    return Response(
                        {
                            'success': "false",
                            'error': 'La hora solicitada no existe',
                            'sugerencia': 'Verifica el ID o intenta con otra hora',
                            'codigo_error': 'HORA_NO_ENCONTRADA'
                        },
                        status=404
                    )

                estado, fecha, hora, id_cesfam = row

                # Validar disponibilidad
                if estado != 'disponible':
                    logger.warning(f'Hora no disponible. Estado actual: {estado}')
                    return Response(
                        {
                            'success': "false",
                            'error': f'La hora ya no está disponible (estado: {estado})',
                            'codigo_error': 'HORA_NO_DISPONIBLE'
                        },
                        status=409
                    )

                # 4. Validar que no sea una hora pasada (CORRECCIÓN DEL ERROR)
                hora_datetime_naive = datetime.combine(fecha, hora)
                hora_datetime_aware = timezone.make_aware(hora_datetime_naive)
                
                if hora_datetime_aware < timezone.now():
                    logger.warning('Intento de reservar hora pasada')
                    return Response(
                        {
                            'success': "false",
                            'error': 'No se puede reservar una hora pasada',
                            'codigo_error': 'HORA_PASADA'
                        },
                        status=400
                    )

                # 5. Verificar reservas existentes del usuario
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM usuario_agenda 
                    WHERE id_manychat_id IN (
                        SELECT id FROM administracion_usuario 
                        WHERE id_manychat = %s
                    )
                    AND fecha_atencion = %s 
                    AND hora_atencion = %s
                """, [manychat_id, fecha, hora])
                
                if cursor.fetchone()[0] > 0:
                    logger.warning('Usuario ya tiene reserva en este horario')
                    return Response(
                        {
                            'success': "false",
                            'error': 'Ya tienes una reserva en este mismo horario',
                            'codigo_error': 'RESERVA_DUPLICADA'
                        },
                        status=400
                    )

                # 6. Llamar al procedimiento almacenado
                cursor.callproc('cambiar_estado_hora', [
                    hora_id,
                    'reservada',
                    manychat_id,
                    None  # OUT parameter
                ])
                cursor.execute("SELECT @_cambiar_estado_hora_3")
                resultado = cursor.fetchone()[0]
                
                if not resultado or resultado.startswith('Error'):
                    logger.error(f'Error en procedimiento almacenado: {resultado}')
                    return Response(
                        {
                            'success': "false",
                            'error': resultado or 'Error al cambiar estado de la hora',
                            'codigo_error': 'ERROR_PROCESAMIENTO'
                        },
                        status=400
                    )

            except DatabaseError as db_error:
                logger.error(f'Error de base de datos: {str(db_error)}')
                return Response(
                    {
                        'success': "false",
                        'error': 'Error al consultar la base de datos',
                        'detalle': str(db_error),
                        'codigo_error': 'ERROR_BD'
                    },
                    status=500
                )

        # 7. Crear registro en Agenda
        try:
            usuario = Usuario.objects.get(id_manychat=manychat_id)
            agenda = Agenda.objects.create(
                fecha_atencion=fecha,
                hora_atencion=hora,
                requisito_examen=requisito_examen,
                id_cesfam_id=id_cesfam,
                id_manychat=usuario,
                id_procedimiento_id=procedimiento_id
            )

            # 8. Actualizar campo agenda_id en la tabla
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuario_horas_agenda
                    SET agenda_id = %s
                    WHERE id_hora = %s
                """, [agenda.id_agenda, hora_id])

            # 9. Preparar respuesta exitosa
            response_data = {
                'success': "true",
                'mensaje': 'Hora reservada correctamente',
                'agenda_id': agenda.id_agenda,
                'fecha': fecha.strftime('%d/%m/%Y'),
                'hora': hora.strftime('%H:%M'),
                'detalles': {
                    'cesfam_id': id_cesfam,
                    'procedimiento_id': procedimiento_id,
                    'usuario_id': usuario.id
                }
            }

            logger.info(f'Reserva exitosa. Agenda ID: {agenda.id_agenda}')
            return Response(response_data, status=201)

        except Usuario.DoesNotExist:
            logger.error(f'Usuario no encontrado: {manychat_id}')
            return Response(
                {
                    'success': "false",
                    'error': 'Usuario no encontrado',
                    'codigo_error': 'USUARIO_NO_ENCONTRADO'
                },
                status=404
            )
        except Exception as e:
            logger.error(f'Error al crear agenda: {str(e)}')
            return Response(
                {
                    'success': "false",
                    'error': 'Error al crear la reserva',
                    'detalle': str(e),
                    'codigo_error': 'ERROR_CREACION_AGENDA'
                },
                status=500
            )

    except Exception as e:
        logger.critical(f'Error inesperado: {str(e)}', exc_info=True)
        return Response(
            {
                'success': "false",
                'error': 'Error inesperado en el servidor',
                'detalle': str(e),
                'codigo_error': 'ERROR_INTERNO'
            },
            status=500
        )
import json
import secrets
from usuario.models import HoraAgenda, Agenda, Recordatorio
from administracion.models import Usuario, LogEnvioEmail
from administracion.services import DivulgacionService, EmailService
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string 
from django.db import connection, transaction, DatabaseError
from datetime import date, datetime, timedelta, time
from django.utils import timezone
from django.utils.timezone import make_aware
import requests
import logging
import hashlib
from .models import *
from .serializer import *
import pytz
from django.db.models import F, Value, ExpressionWrapper, DateTimeField
from django.db.models.functions import Concat, Cast
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


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
    try:
        if not request.data:
            logger.warning("Request sin datos recibido")
            return Response(
                {'error': 'Datos de solicitud requeridos', 'completo': 'false'},
                status=status.HTTP_200_OK  
            )
        
        id_manychat = request.data.get('id_manychat', '').strip()
        if not id_manychat:
            logger.warning("Request sin id_manychat")
            return Response(
                {'error': 'El campo id_manychat es requerido', 'completo': 'false'},
                status=status.HTTP_200_OK
            )

        try:
            usuario = Usuario.objects.get(id_manychat=id_manychat)
            logger.info(f"Usuario encontrado: {id_manychat}")
        except ObjectDoesNotExist:
            logger.info(f"Usuario no encontrado: {id_manychat}")
            return Response(
                {
                    'completo': 'false',
                    'estado': 'usuario_no_registrado',
                    'mensaje': 'Usuario no registrado en el sistema'
                },
                status=status.HTTP_200_OK
            )
            
        tipos = ['TM', 'DS', 'FRM', 'FRNM']
        cuestionarios_pendientes = []
        
        for tipo in tipos:
            if not verificar_tipo_completo(usuario, tipo):
                cuestionarios_pendientes.append(tipo)

        if not cuestionarios_pendientes:
            logger.info(f"Usuario {id_manychat} tiene todos los cuestionarios completos")
            return Response(
                {
                    'completo': 'true',
                    'estado': 'completo',
                    'mensaje': 'Todos los cuestionarios están completos'
                },
                status=status.HTTP_200_OK
            )
        
        logger.info(f"Usuario {id_manychat} tiene cuestionarios pendientes: {cuestionarios_pendientes}")
        return Response(
            {
                'completo': 'false',
                'estado': 'cuestionarios_pendientes',
                'pendientes': ','.join(cuestionarios_pendientes),
                'mensaje': f"Cuestionarios pendientes: {', '.join(cuestionarios_pendientes)}"
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Error en el servidor',
                'completo': 'false',
                'estado': 'error_interno'
            },
            status=status.HTTP_200_OK 
        )

def verificar_tipo_completo(usuario, tipo):
    #Verifica si un usuario respondió todas las preguntas de un tipo específico
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

from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging

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
    return fecha.strftime("%d-%m") in FERIADOS_FIJOS

def obtener_dia_habil_siguiente(fecha):
    while True:
        fecha += timedelta(days=1)
        if fecha.weekday() >= 5:
            continue
        if es_feriado(fecha):
            continue
        return fecha

@api_view(['POST'])
def horas_disponibles(request):
    try:
        data = request.data
        cesfam_id = data.get('cesfam_id')
        
        if not cesfam_id:
            return Response({'error': 'Se requiere cesfam_id'}, status=400)
        
        hoy = datetime.now().date()
        fecha_busqueda = obtener_dia_habil_siguiente(hoy)
        horas_disponibles = []
        dias_buscados = 0
        max_dias_busqueda = 14  
        
        while len(horas_disponibles) < 3 and dias_buscados < max_dias_busqueda:
            # Buscar horas disponibles para este día
            horas_del_dia = HoraAgenda.objects.filter(
                fecha=fecha_busqueda,
                estado='disponible',
                cesfam_id=cesfam_id
            ).order_by('hora')
            
            for hora in horas_del_dia:
                if len(horas_disponibles) >= 3:
                    break
                
                horas_disponibles.append({
                    'hora_id': str(hora.id_hora), 
                    'display_text': f"{hora.fecha.strftime('%d/%m/%Y')} {hora.hora.strftime('%H:%M')}",
                    'fecha': hora.fecha.strftime('%d/%m/%Y'),
                    'hora': hora.hora.strftime('%H:%M'),
                })
            
            dias_buscados += 1
            fecha_busqueda = obtener_dia_habil_siguiente(fecha_busqueda)
        
        return Response({
            'horas_disponibles': horas_disponibles[:3],
            'fecha_consulta': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'cache': False
        })
        
    except Exception as e:
        logger.error(f"Error en horas_disponibles: {str(e)}", exc_info=True)
        return Response({'error': 'Error al obtener horas disponibles'}, status=500)


import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@transaction.atomic
def reservar_hora(request):
    try:
        data = request.data
        hora_id = data.get('hora_id')
        manychat_id = data.get('manychat_id')
        requisito_examen = data.get('requisito_examen', '')
        procedimiento_id = data.get('procedimiento_id')
        email_paciente = data.get('email')

        if not all([hora_id, manychat_id, procedimiento_id, email_paciente]):
            return Response({'success': "false", 'error': 'Datos incompletos',
                           'codigo_error': 'DATOS_INCOMPLETOS'}, status=400)

        with connection.cursor() as cursor:
            try:
                # Verificar y bloquear la hora
                cursor.execute("""
                    SELECT estado, fecha, hora, id_cesfam 
                    FROM usuario_horas_agenda 
                    WHERE id_hora = %s
                    FOR UPDATE
                """, [hora_id])
                row = cursor.fetchone()
                
                if not row:
                    return Response({'success': "false", 'error': 'La hora solicitada no existe',
                                   'codigo_error': 'HORA_NO_ENCONTRADA'}, status=404)

                estado, fecha, hora, id_cesfam = row

                if estado != 'disponible':
                    return Response({'success': "false", 'error': f'La hora ya no está disponible (estado: {estado})',
                                   'codigo_error': 'HORA_NO_DISPONIBLE'}, status=409)

                hora_datetime = make_aware(datetime.combine(fecha, hora))
                if hora_datetime < timezone.now():
                    return Response({'success': "false", 'error': 'No se puede reservar una hora pasada',
                                   'codigo_error': 'HORA_PASADA'}, status=400)

                # Verificar reserva duplicada
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM usuario_agenda 
                    WHERE id_manychat_id = %s
                    AND fecha_atencion = %s 
                    AND hora_atencion = %s
                """, [manychat_id, fecha, hora])
                
                if cursor.fetchone()[0] > 0:
                    return Response({'success': "false", 'error': 'Ya tienes una reserva en este mismo horario',
                                   'codigo_error': 'RESERVA_DUPLICADA'}, status=400)

                # Cambiar estado de la hora
                cursor.callproc('cambiar_estado_hora', [hora_id, 'reservada', manychat_id, None])
                cursor.execute("SELECT @_cambiar_estado_hora_3")
                resultado = cursor.fetchone()[0]

                if not resultado or resultado.startswith('Error'):
                    return Response({'success': "false", 'error': resultado or 'Error al cambiar estado de la hora',
                                   'codigo_error': 'ERROR_PROCESAMIENTO'}, status=400)

                try:
                    usuario = Usuario.objects.get(id_manychat=manychat_id)
                    
                    # Crear agenda sin usar agenda_id en usuario_horas_agenda
                    agenda = Agenda.objects.create(
                        fecha_atencion=fecha,
                        hora_atencion=hora,
                        requisito_examen=requisito_examen,
                        id_cesfam_id=id_cesfam,
                        id_manychat=usuario,
                        id_procedimiento_id=procedimiento_id
                    )

                    # Crear recordatorio usando solo el ID de agenda
                    fecha_recordatorio = hora_datetime - timedelta(hours=6)
                    try:
                        cursor.execute("""
                            INSERT INTO recordatorios_programados 
                            (agenda_id, email, enviado, fecha_programada, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [
                            agenda.id_agenda,
                            email_paciente,
                            False,
                            fecha_recordatorio,
                            timezone.now()
                        ])
                    except Exception as e:
                        logger.error("Error al crear el recordatorio: %s", str(e))
                        # No falla la operación completa si falla el recordatorio

                    return Response({
                        'success': "true",
                        'mensaje': 'Hora reservada correctamente',
                        'agenda_id': agenda.id_agenda,
                        'fecha': fecha.strftime('%d/%m/%Y'),
                        'hora': hora.strftime('%H:%M')
                    }, status=201)

                except Usuario.DoesNotExist:
                    return Response({'success': "false", 'error': 'Usuario no encontrado',
                                   'codigo_error': 'USUARIO_NO_ENCONTRADO'}, status=404)
                except Exception as e:
                    return Response({'success': "false", 'error': 'Error al crear la reserva',
                                   'detalle': str(e), 'codigo_error': 'ERROR_CREACION_AGENDA'}, status=500)

            except DatabaseError as db_error:
                return Response({'success': "false", 'error': 'Error al consultar la base de datos',
                               'detalle': str(db_error), 'codigo_error': 'ERROR_BD'}, status=500)

    except Exception as e:
        return Response({'success': "false", 'error': 'Error inesperado en el servidor',
                       'detalle': str(e), 'codigo_error': 'ERROR_INTERNO'}, status=500)

@csrf_exempt
@api_view(['POST'])
def verificar_reserva(request):
    try:
        data = json.loads(request.body)
        hora_id = data.get('hora_id')
        id_manychat = data.get('id_manychat')
        
        if not all([hora_id, id_manychat]):
            return JsonResponse({"reservado": "false", "error": "Missing parameters"}, status=400)
        
        hora_agenda = HoraAgenda.objects.filter(id_hora=hora_id).first()
        
        if not hora_agenda:
            return JsonResponse({"reservado": "false", "error": "Slot not found"})
        
        reservado = hora_agenda.estado == 'reservada' and hora_agenda.id_manychat == id_manychat

        return JsonResponse({
            "reservado": "true" if reservado else "false",
            "hora_id": str(hora_id),
            "id_manychat": str(id_manychat)
        })
            
    except Exception as e:
        return JsonResponse({"reservado": "false", "error": str(e)}, status=500)
    
logger = logging.getLogger(__name__)


@api_view(['POST'])
def verificar_habilitado_para_reservar(request):
    try:
        data = request.data
        manychat_id = data.get('manychat_id')

        if not manychat_id:
            return Response({
                'success': "false", 
                'error': 'ID de usuario requerido',
                'codigo_error': 'ID_USUARIO_REQUERIDO'
            }, status=400)

        with connection.cursor() as cursor:
            # Verificar citas activas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM usuario_horas_agenda 
                WHERE id_manychat = %s
                AND (fecha > CURRENT_DATE OR 
                    (fecha = CURRENT_DATE AND hora > CURRENT_TIME))
                AND estado NOT IN ('cancelada', 'completada')
            """, [manychat_id])
            
            tiene_citas_activas = cursor.fetchone()[0] > 0
            
            return Response({
                'success': "true",
                'puede_reservar': "false" if tiene_citas_activas else "true",
                'mensaje': 'Ya tienes una cita activa' if tiene_citas_activas 
                          else 'Usuario habilitado para reservar',
                'codigo_estado': 'CITA_ACTIVA' if tiene_citas_activas 
                               else 'HABILITADO_PARA_RESERVA'
            })

    except Exception as e:
        logger.error(f"Error en verificar_habilitado_para_reservar: {str(e)}")
        return Response({
            'success': "false", 
            'error': 'Error interno del servidor',
            'detalle_error': str(e),
            'codigo_error': 'ERROR_INTERNO'
        }, status=500)

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def enviar_recordatorios_pendientes(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        logger.error("Falta header de Authorization")
        return Response({'error': 'Se requiere token de autenticación'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not hasattr(settings, 'GITHUB_WEBHOOK_SECRET'):
        logger.error("GITHUB_WEBHOOK_SECRET no está configurado en settings")
        return Response({'error': 'Configuración del servidor incompleta'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    auth_header = auth_header.strip()
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0] != 'Token':
        logger.error(f"Formato de token inválido. Header recibido: {auth_header}")
        return Response({'error': 'Formato de autorización inválido. Use: Token <token>'}, status=status.HTTP_401_UNAUTHORIZED)
    
    received_token = parts[1].strip()
    expected_token = settings.GITHUB_WEBHOOK_SECRET.strip()
    
    if not secrets.compare_digest(received_token, expected_token):
        logger.error("Token no coincide")
        return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        tz_chile = pytz.timezone('America/Santiago')
        ahora_chile = timezone.now().astimezone(tz_chile)
        
        fecha_actual = ahora_chile.date()
        
        if ahora_chile.hour == 7 and ahora_chile.minute <= 25:
            hora_inicio = time(8, 0)
            hora_fin = time(14, 59)
            tipo_recordatorio = "mañana"
        elif ahora_chile.hour == 15  and ahora_chile.minute <= 25:
            hora_inicio = time(15, 0)
            hora_fin = time(23, 0)
            tipo_recordatorio = "tarde"
        else:
            return Response({'status': 'skipped', 'reason': 'Hora no programada'})

        citas_pendientes = Agenda.objects.filter(
            fecha_atencion=fecha_actual,  
            hora_atencion__gte=hora_inicio,
            hora_atencion__lte=hora_fin
        ).exclude(
            recordatorio__enviado=1  
        )

        enviados = 0
        for cita in citas_pendientes:
            recordatorio, created = Recordatorio.objects.get_or_create(
                agenda=cita,
                defaults={
                    'email': cita.id_manychat.email,
                    'fecha_programada': timezone.now(),
                    'enviado': 0
                }
            )
            
            if recordatorio.enviado == 0:
                enviar_email_recordatorio(recordatorio)
                recordatorio.enviado = 1
                recordatorio.save()
                enviados += 1

        return Response({
            'status': 'success',
            'enviados': enviados,
            'total_citas': len(citas_pendientes),
            'detalle': f"Recordatorios {tipo_recordatorio} para citas el {fecha_actual.strftime('%d/%m/%Y')} entre {hora_inicio}-{hora_fin}"
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def enviar_email_recordatorio(recordatorio):
    agenda = recordatorio.agenda
    context = {
        'fecha': agenda.fecha_atencion.strftime('%d/%m/%Y'),
        'hora': agenda.hora_atencion.strftime('%H:%M'),
        'cesfam': agenda.id_cesfam.nombre_cesfam,
        'requisitos': agenda.requisito_examen
    }

    email = EmailMultiAlternatives(
        subject=f"Recordatorio: Cita en {agenda.id_cesfam.nombre_cesfam}",
        body=render_to_string('emails/recordatorio.txt', context),
        from_email='redtamicervicouterino@gmail.com',
        to=[recordatorio.email],
    )
    email.attach_alternative(
        render_to_string('emails/recordatorio.html', context),
        "text/html"
    )
    email.send()

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def enviar_divulgaciones(request):
    # Validar token secreto en header Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logger.error("Falta header de Authorization")
        return Response({'error': 'Se requiere token de autenticación'}, status=status.HTTP_401_UNAUTHORIZED)
    
    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0] != 'Token':
        logger.error(f"Formato de token inválido. Header recibido: {auth_header}")
        return Response({'error': 'Formato de autorización inválido. Use: Token <token>'}, status=status.HTTP_401_UNAUTHORIZED)
    
    received_token = parts[1].strip()
    expected_token = getattr(settings, 'GITHUB_WEBHOOK_SECRET', '').strip()

    if not expected_token:
        logger.error("GITHUB_WEBHOOK_SECRET no está configurado en settings")
        return Response({'error': 'Configuración del servidor incompleta'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if not secrets.compare_digest(received_token, expected_token):
        logger.error("Token no coincide")
        return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        divulgacion = DivulgacionService.obtener_divulgacion_pendiente()
        if not divulgacion:
            return Response({"status": "skip", "detail": "No hay divulgaciones pendientes"}, status=200)
        
        usuarios = DivulgacionService.obtener_usuarios_optin()
        if not usuarios.exists():
            return Response({"status": "skip", "detail": "No hay usuarios opt-in con email válido"}, status=200)
        
        resultados = []
        for usuario in usuarios:
            email_obj = DivulgacionService.construir_email(divulgacion, usuario)
            respuesta = EmailService.enviar_email(email_obj)
            
            LogEnvioEmail.objects.create(
                usuario=usuario,
                divulgacion=divulgacion,
                exito=respuesta.get('status') == 'success',
                error=respuesta.get('message') if respuesta.get('status') == 'error' else None,
                direccion_email=usuario.email
            )
            
            resultados.append({
                "usuario": usuario.id_manychat,
                "email": usuario.email,
                "status": respuesta.get('status')
            })
        
        divulgacion.enviada = True
        divulgacion.fecha_envio = timezone.now()
        divulgacion.save()
        
        return Response({
            "status": "success",
            "divulgacion_id": divulgacion.id_divulgacion,
            "enviados": len(resultados),
            "detalle": resultados
        })
    
    except Exception as e:
        logger.error(f"Error en enviar_divulgaciones: {str(e)}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def baja_usuario(request, id_manychat):
    try:
        usuario = get_object_or_404(Usuario, id_manychat=id_manychat)
        usuario.opt_out = True
        usuario.save()
        
        return render(request, 'divulgacion/baja_confirmacion.html', {
            'usuario': usuario,
            'fecha': timezone.now().date()
        })
        
    except Exception as e:
        logger.error(f"Error en baja_usuario: {str(e)}")
        return HttpResponse("Ocurrió un error al procesar tu solicitud", status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_perfil_usuario(request):
    if not request.data or 'id_manychat' not in request.data:
        return Response(
            {'registrado': 'false', 'error': 'id_manychat es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    id_manychat = request.data['id_manychat']

    try:
        # Convertir a entero si es necesario
        try:
            id_manychat_int = int(id_manychat)
        except ValueError:
            id_manychat_int = id_manychat

        # Buscar directamente en PerfilUsuario
        perfil = PerfilUsuario.objects.filter(usuario_sist_id=id_manychat_int).first()
        
        if perfil:
            return Response({
                'registrado': 'true'
            })
        
        # Búsqueda alternativa por si acaso
        usuario_manychat = Usuario.objects.filter(id_manychat=str(id_manychat_int)).first()
        if usuario_manychat and hasattr(usuario_manychat, 'perfilusuario'):
            perfil = usuario_manychat.perfilusuario
            return Response({
                'registrado': 'true',
                'nombre_completo': perfil.user.get_full_name(),
                'email': perfil.user.email,
                'fecha_registro': perfil.user.date_joined,
                'tipo_usuario': perfil.tipo_usuario
            })

        return Response({
            'registrado': 'false',
            'error': 'Usuario no registrado en el sistema'
        })

    except Exception as e:
        return Response({
            'registrado': 'false',
            'error': f'Error en la verificación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

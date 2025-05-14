from django.shortcuts import render
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
from datetime import date
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
    """
    Verifica si un usuario ha respondido todas las preguntas de todos los tipos
    """
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

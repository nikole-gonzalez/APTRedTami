from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    TMViewSet,
    UsuarioTextoPreguntaViewSet,
    DivulgacionViewSet,
    FRNMViewSet,
    FRMViewSet,
    DSViewSet,
    UsuarioAPIView,
    UsuarioRespuestaTMAPIView,
    UsuarioTextoPreguntaAPIView,
    DivulgacionAPIView,
    UsuarioRespuestFRNMaAPIView,
    UsuarioRespuestFRMaAPIView,
    ObtenerID,
    DivulgacionAPIView,

    apiHome,
    obtener_usuario,
    consultar_estado_pregunta,
    retorna_genero,
    verificar_usuario,
    cuestionario_completo,
    horas_disponibles,
    reservar_hora, 
    verificar_reserva,
    enviar_recordatorios_pendientes,
    verificar_habilitado_para_reservar
)

app_name = 'api'  

# Registramos los ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'TM', TMViewSet)
router.register(r'textos', UsuarioTextoPreguntaViewSet)
router.register(r'divulgacion', DivulgacionViewSet)
router.register(r'frnm', FRNMViewSet)
router.register(r'frm', FRMViewSet)
router.register(r'ds', DSViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('usuarios-api/', UsuarioAPIView.as_view(), name='usuarios-api'),
    path('respuestas-api/', UsuarioRespuestaTMAPIView.as_view(), name='respuestas-api'),
    path('textos-api/', UsuarioTextoPreguntaAPIView.as_view(), name='textos-api'),
    path('frnm-api/', UsuarioRespuestFRNMaAPIView.as_view(), name='frnm-api'),
    path('frm-api/', UsuarioRespuestFRMaAPIView.as_view(), name='frm-api'),
    path('divulgacion/', DivulgacionAPIView.as_view(), name='divulgacion-api'),
    path('obtener-id/', ObtenerID.as_view(), name='obtener-id'),
    path('home/', apiHome, name='api-home'),
    path('obtener-usuario/<int:usuario_id>/', obtener_usuario, name='obtener-usuario'),
    path('consultar-estado-pregunta/', consultar_estado_pregunta, name='consultar-estado-pregunta'),
    path('retorna-genero/', retorna_genero, name='retorna-genero'),
    path('verificar-usuario/', verificar_usuario, name='verificar-usuario'),
    path('cuestionariocompleto/', cuestionario_completo, name='cuestionario_completo'),
    path('horas-disponibles/', horas_disponibles, name='horas-disponibles'),
    path('reservar-hora/', reservar_hora, name='reservar_hora'),
    path('verificar-reserva/', verificar_reserva, name='verificar_reserva'),
    path('enviar-recordatorios/', enviar_recordatorios_pendientes, name='enviar_recordatorios'),
    path('habilitar-reserva/', verificar_habilitado_para_reservar, name='habilitar_reserva'),

]

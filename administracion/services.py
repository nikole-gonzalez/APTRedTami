from django.utils import timezone
from .models import Divulgacion, Usuario, PregTM, OpcTM, LogEnvioEmail
import logging
import requests
from django.conf import settings
import json
from django.template.loader import render_to_string
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

class DivulgacionService:

    @classmethod
    def obtener_divulgacion_pendiente(cls):
        try:
            return Divulgacion.objects.filter(
                activa=True,
                enviada=False  
            ).latest('fecha_creacion', 'id_divulgacion') 
        except Divulgacion.DoesNotExist:
            logger.info("No hay divulgaciones pendientes para enviar")
            return None
        except Exception as e:
            logger.error(f"Error al obtener divulgación pendiente: {str(e)}")
            return None

    @classmethod
    def obtener_usuarios_optin(cls):
        try:
            return Usuario.objects.filter(
                opt_out=False,
                resptm__id_opc_tm__id_preg_tm__cod_pregunta_tm="TM6",  
                resptm__id_opc_tm__id_opc_tm=17,
                email__isnull=False
            ).exclude(email__exact='').distinct()
            
        except Exception as e:
            logger.error(f"Error al filtrar usuarios: {str(e)}")
            return Usuario.objects.none()

    @classmethod
    def construir_email(cls, divulgacion, usuario):
        if not usuario.email:
            raise ValueError(f"Usuario {usuario.id_manychat} no tiene email válido")

        context = {
            'divulgacion': divulgacion,
            'usuario': usuario,
            'opt_out_url': f"{settings.BASE_URL}/API/baja/{usuario.id_manychat}"
        }

        html_content = render_to_string('divulgacion/email_template.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f"📢 {divulgacion.asunto if hasattr(divulgacion, 'asunto') else 'Mensaje de salud'}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[usuario.email],
            reply_to=[settings.REPLY_TO_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")

        if divulgacion.imagen_url and hasattr(divulgacion, 'imagen') and divulgacion.imagen:
            email.attach_file(divulgacion.imagen.path)

        return email


class EmailService:
    @staticmethod
    def enviar_email(email_obj):
        try:
            email_obj.send()
            return {
                "status": "success",
                "message": "Email enviado correctamente"
            }
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
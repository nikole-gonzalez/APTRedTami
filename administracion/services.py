from django.utils import timezone
from .models import Divulgacion, Usuario, PregTM, OpcTM, LogEnvioWhatsApp
import logging
import requests
from django.conf import settings
import json

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
                id_manychat__isnull=False
            ).distinct()
        except Exception as e:
            logger.error(f"Error al obtener usuarios opt-in: {str(e)}")
            return Usuario.objects.none()

    @classmethod
    def construir_mensaje(cls, divulgacion):
        mensaje = {
            "messages": [
                {
                    "type": "text",
                    "text": f"📢 Mensaje de salud:\n\n{divulgacion.texto_divulgacion}\n\n🔗 Más información: {divulgacion.url}"
                }
            ],
            "quick_replies": [
                {
                    "title": "📚 Ver más información",
                    "payload": "VER_MAS"
                },
                {
                    "title": "🚫 No recibir más",
                    "payload": "BAJA"
                }
            ],
            "message_tag": "ACCOUNT_UPDATE"
        }
        
        if divulgacion.imagen_url:
            mensaje['messages'].insert(0, {
                "type": "image",
                "url": divulgacion.imagen_url
            })
            
        return mensaje

class ManyChatService:
    @staticmethod
    def enviar_mensaje(id_manychat, message_data):
        api_url = "https://api.manychat.com/fb/sending/sendContent"
        headers = {
            "Authorization": f"Bearer {settings.MANYCHAT_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "subscriber_id": str(id_manychat),
            "data": {
                "version": "v2",
                "content": {
                    "messages": message_data["messages"],
                    "quick_replies": message_data.get("quick_replies", [])
                }
            },
            "message_tag": message_data.get("message_tag", "ACCOUNT_UPDATE")
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Error ManyChat: {str(e)}"
            if e.response:
                error_msg += f" | Status: {e.response.status_code} | Response: {e.response.text}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "status_code": e.response.status_code if e.response else None
            }
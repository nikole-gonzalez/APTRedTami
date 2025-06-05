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
            ).latest('fecha_creacion', 'id')  
        
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
                resptm__id_opc_tm__id_opc_tm=17  
            ).distinct()
            
        except Exception as e:
            logger.error(f"Error al filtrar usuarios: {str(e)}")
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
                    "type": "text",
                    "title": "📚 Ver más información", 
                    "payload": divulgacion.url,  
                    "url": divulgacion.url
                },
                {
                    "type": "text",
                    "title": "🚫 No quiero recibir más mensajes",
                    "payload": "BAJA"  
                }
            ]
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
        """
        Versión corregida compatible con API v2
        """
        api_url = "https://api.manychat.com/fb/sending/sendContent"
        headers = {
            "Authorization": f"Bearer {settings.MANYCHAT_API_KEY}",
            "Content-Type": "application/json"
        }

        quick_replies = []
        for qr in message_data.get("quick_replies", []):
            quick_replies.append({
                "type": qr["type"],
                "title": qr.get("caption", qr.get("title", "")),  
                "payload": qr.get("content", qr.get("payload", "")),  
                "url": qr.get("url", None)
            })

        payload = {
            "subscriber_id": str(id_manychat),
            "data": {
                "version": "v2",
                "content": {
                    "messages": message_data["messages"],
                    "quick_replies": quick_replies
                }
            }
        }

        try:
            logger.debug("Payload a ManyChat:\n%s", json.dumps(payload, indent=2))
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Error {e.response.status_code if e.response else 'N/A'}: {str(e)}"
            if e.response:
                error_msg += f"\nResponse: {e.response.text}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "status_code": e.response.status_code if e.response else None
            }
from django.utils import timezone
from .models import Divulgacion, Usuario, PregTM, OpcTM, LogEnvioWhatsApp
import logging
import requests
from django.conf import settings

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
                    "text": (
                        f"📢 Mensaje de salud:\n\n"
                        f"{divulgacion.texto_divulgacion}\n\n"
                        f"🔗 Más información: {divulgacion.url}"
                    )
                }
            ],
            "quick_replies": [
                {
                    "type": "text",
                    "caption": "📚 Ver más información",
                    "url": divulgacion.url
                },
                {
                    "type": "text",
                    "caption": "🚫 No quiero recibir más mensajes",
                    "content": "BAJA"
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
    def enviar_mensaje(user_id, message_data):
        api_url = "https://api.manychat.com/fb/sending/sendContent"
        
        headers = {
            "Authorization": f"Bearer {settings.MANYCHAT_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "subscriber_id": id_manychat,
            "data": message_data
        }

        try:
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            error_msg = f"Error HTTP {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "status_code": response.status_code
            }
        except Exception as e:
            logger.error(f"Error de conexión: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
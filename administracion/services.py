from django.utils import timezone
from .models import Divulgacion, Usuario, PregTM, OpcTM, LogEnvioWhatsApp
import logging

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
            # Versión mejorada con manejo explícito de relaciones
            return Usuario.objects.filter(
                opt_out=False,
                resptm__id_opc_tm__id_preg_tm__cod_pregunta_tm="TM6",  # Corregida la sintaxis
                resptm__id_opc_tm__id_opc_tm=17  # Corregida la sintaxis
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
    def enviar_mensaje(user_id, message):
        """
        Envía un mensaje a través de ManyChat API
        Args:
            user_id (str): ID del usuario en ManyChat
            message (dict): Estructura del mensaje en formato ManyChat
        Returns:
            dict: Respuesta de la API ManyChat
        """
        import requests
        from django.conf import settings
        
        headers = {
            "Authorization": f"Bearer {settings.MANYCHAT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "subscriber_id": user_id,
            "data": message
        }
        
        try:
            response = requests.post(
                "https://api.manychat.com/fb/sending/sendContent",
                json=payload,
                headers=headers,
                timeout=10  
            )
            response.raise_for_status()  
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar a ManyChat: {str(e)}")
            return {
                "status": "error",
                "errors": str(e)
            }
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_para_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        if not hasattr(instance, 'perfilusuario'):
            PerfilUsuario.objects.create(
                user=instance,
                tipo_usuario='administrador',
                rut_usuario=99999999,
                dv_rut='9',
                telefono=0
            )
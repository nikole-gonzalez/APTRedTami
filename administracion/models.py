from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import encrypt_data, decrypt_data

class PerfilUsuario(models.Model):
    id_perfil = models.AutoField(primary_key=True, verbose_name="Id Perfil")
    telefono = models.TextField(null=True, blank=True) 
    rut_usuario = models.TextField(null=True, blank=True) 
    dv_rut = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    usuario_sist = models.OneToOneField('Usuario', on_delete=models.CASCADE, null=True, blank=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[('administrador', 'Administrador'), ('paciente', 'Paciente')],
        default='paciente'
    )

    def get_telefono_descifrado(self):
        """Obtiene el teléfono descifrado"""
        return decrypt_data(self.telefono) if self.telefono else None
    
    def get_rut_descifrado(self):
        """Obtiene el RUT descifrado"""
        return decrypt_data(self.rut_usuario) if self.rut_usuario else None
    
    def get_dv_descifrado(self):
        """Obtiene el DV descifrado"""
        return decrypt_data(self.dv_rut) if self.dv_rut else None
    
    def get_rut_completo_descifrado(self):
        """Obtiene RUT completo (con guión) descifrado"""
        rut = self.get_rut_descifrado()
        dv = self.get_dv_descifrado()
        return f"{rut}-{dv}" if rut and dv else None

    def save(self, *args, **kwargs):
        if self.telefono and not self.telefono.startswith('gAAAA'):
            self.telefono = encrypt_data(str(self.telefono))
        
        if self.rut_usuario and not self.rut_usuario.startswith('gAAAA'):
            self.rut_usuario = encrypt_data(str(self.rut_usuario))
        
        if self.dv_rut and not self.dv_rut.startswith('gAAAA'):
            self.dv_rut = encrypt_data(str(self.dv_rut))
        
        super().save(*args, **kwargs)

    def __str__(self):
        rut = self.get_rut_completo_descifrado() or "sin_rut"
        return f"{self.user.username} - {rut}"
    
class Usuario(models.Model):
    id_manychat = models.CharField(primary_key=True, max_length=20, verbose_name="Id Manychat")
    rut_usuario = models.TextField()
    dv_rut = models.CharField(max_length=255, null=True, blank=True)  
    fecha_nacimiento = models.DateTimeField()
    num_whatsapp = models.TextField() 
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cod_comuna = models.ForeignKey('Comuna', on_delete=models.CASCADE)
    email = models.TextField(blank=True) 
    cesfam_usuario = models.ForeignKey('usuario.Cesfam', on_delete=models.CASCADE, null=True, blank=True)
    opt_out = models.BooleanField(
        default=False,
        verbose_name="No recibir mensajes",
        help_text="Si está marcado, el usuario no recibirá mensajes de divulgación"
    )

    def get_rut_descifrado(self):
        return decrypt_data(self.rut_usuario) if self.rut_usuario else None
    
    def get_dv_descifrado(self):
        return decrypt_data(self.dv_rut) if self.dv_rut else None
    
    def get_whatsapp_descifrado(self):
        return decrypt_data(self.num_whatsapp) if self.num_whatsapp else None
    
    def get_email_descifrado(self):
        return decrypt_data(self.email) if self.email else None
    
    def get_rut_completo_descifrado(self):
        rut = self.get_rut_descifrado()
        dv = self.get_dv_descifrado()
        return f"{rut}-{dv}" if rut and dv else None

    def save(self, *args, **kwargs):
        """Cifra los datos antes de guardar"""
        if self.rut_usuario:
            self.rut_usuario = str(self.rut_usuario)
            if not self.rut_usuario.startswith('gAAAA'):
                self.rut_usuario = encrypt_data(self.rut_usuario)
        
        if self.dv_rut:
            self.dv_rut = str(self.dv_rut)
            if not self.dv_rut.startswith('gAAAA'):
                self.dv_rut = encrypt_data(self.dv_rut)
        
        if self.num_whatsapp:
            self.num_whatsapp = str(self.num_whatsapp)
            if not self.num_whatsapp.startswith('gAAAA'):
                self.num_whatsapp = encrypt_data(self.num_whatsapp)
        
        if self.email:
            self.email = str(self.email)
            if not self.email.startswith('gAAAA'):
                self.email = encrypt_data(self.email)
        
        super().save(*args, **kwargs)

    def __str__(self):
        rut = self.get_rut_completo_descifrado() or "rut-dv"
        return f"Usuario: {rut} ({self.id_manychat})"
    
    def cuestionario_completo(self):
        tipos = [
            ('TM', RespTM, PregTM, 'id_opc_tm__id_preg_tm'),
            ('DS', RespDS, PregDS, 'id_opc_ds__id_preg_ds'),
            ('FRM', RespFRM, PregFRM, 'id_opc_frm__id_preg_frm'),
            ('FRNM', RespFRNM, PregFRNM, 'id_opc_frnm__id_preg_frnm')
        ]
        
        for tipo, modelo_resp, modelo_preg, relacion in tipos:
            if not modelo_resp.objects.filter(id_manychat=self).exists():
                return 'false'
                
            total = modelo_preg.objects.count()
            respondidas = modelo_resp.objects.filter(
                id_manychat=self
            ).values_list(relacion, flat=True).distinct().count()
            
            if respondidas < total:
                return 'false'
                
        return 'true'

class Region(models.Model):
    cod_region = models.IntegerField(primary_key=True, verbose_name= "Cod region")
    nombre_region = models.CharField(max_length=200)

    def __str__(self):
        return f"Región {self.cod_region}: {self.nombre_region}"

class Provincia(models.Model):
    cod_provincia = models.IntegerField(primary_key=True, verbose_name= "Cod provincia")
    nombre_provincia = models.CharField(max_length=200)
    cod_region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return f"Provincia {self.cod_provincia}: {self.nombre_provincia} ({self.cod_region})"

class Comuna(models.Model):
    cod_comuna = models.IntegerField(primary_key=True, verbose_name= "Cod comuna")
    nombre_comuna = models.CharField(max_length=200)
    cod_provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comuna {self.cod_comuna}: {self.nombre_comuna}"

class UsuarioTextoPregunta(models.Model):
    id_texto_preg = models.AutoField(primary_key=True)
    texto_pregunta = models.CharField(max_length=200)
    fecha_pregunta_texto = models.DateTimeField(auto_now_add=True)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pregunta textual #{self.id_texto_preg} de {self.id_manychat}"

class PregTM(models.Model):
    id_preg_tm = models.AutoField(primary_key=True)
    preg_tm = models.CharField(max_length=200)
    cod_pregunta_tm = models.CharField(max_length=8)

    def __str__(self):
        return self.preg_tm

class OpcTM(models.Model):
    id_opc_tm = models.AutoField(primary_key=True)
    opc_resp_tm = models.CharField(max_length=200)
    id_preg_tm = models.ForeignKey(PregTM, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_preg_tm} - {self.opc_resp_tm}"

class RespTM(models.Model):
    id_resp_tm = models.AutoField(primary_key=True)
    fecha_respuesta_tm = models.DateTimeField(auto_now_add=True)
    id_opc_tm = models.ForeignKey(OpcTM, on_delete=models.CASCADE)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_opc_tm}"

class PregDS(models.Model):
    id_preg_ds = models.AutoField(primary_key=True)
    preg_ds = models.CharField(max_length=200)
    cod_pregunta_ds = models.CharField(max_length=8)

    def __str__(self):
        return self.preg_ds

class OpcDS(models.Model):
    id_opc_ds = models.AutoField(primary_key=True)
    opc_resp_ds = models.CharField(max_length=200)
    id_preg_ds = models.ForeignKey(PregDS, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_preg_ds} - {self.opc_resp_ds}"

class RespDS(models.Model):
    id_resp_ds = models.AutoField(primary_key=True)
    fecha_respuesta_ds = models.DateTimeField(auto_now_add=True)
    id_opc_ds = models.ForeignKey(OpcDS, on_delete=models.CASCADE)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_opc_ds}"

class PregFRM(models.Model):
    id_preg_frm = models.AutoField(primary_key=True)
    preg_frm = models.CharField(max_length=200)
    cod_pregunta_frm = models.CharField(max_length=8)

    def __str__(self):
        return self.preg_frm

class OpcFRM(models.Model):
    id_opc_frm = models.AutoField(primary_key=True)
    opc_resp_frm = models.CharField(max_length=200)
    id_preg_frm = models.ForeignKey(PregFRM, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_preg_frm} - {self.opc_resp_frm}"

class RespFRM(models.Model):
    id_resp_frm = models.AutoField(primary_key=True)
    fecha_respuesta_frm = models.DateTimeField(auto_now_add=True)
    id_opc_frm = models.ForeignKey(OpcFRM, on_delete=models.CASCADE)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_opc_frm}"

class PregFRNM(models.Model):
    id_preg_frnm = models.AutoField(primary_key=True)
    preg_frnm = models.CharField(max_length=200)
    cod_pregunta_frnm = models.CharField(max_length=8)

    def __str__(self):
        return self.preg_frnm

class OpcFRNM(models.Model):
    id_opc_frnm = models.AutoField(primary_key=True)
    opc_resp_frnm = models.CharField(max_length=200)
    id_preg_frnm = models.ForeignKey(PregFRNM, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_preg_frnm} - {self.opc_resp_frnm}"

class RespFRNM(models.Model):
    id_resp_frnm = models.AutoField(primary_key=True)
    fecha_respuesta_frnm = models.DateTimeField(auto_now_add=True)
    id_opc_frnm = models.ForeignKey(OpcFRNM, on_delete=models.CASCADE)
    id_manychat = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id_opc_frnm}"

class Divulgacion(models.Model):
    id_divulgacion = models.AutoField(primary_key=True)
    texto_divulgacion = models.CharField(max_length=200)
    url = models.URLField()
    imagen_url = models.URLField(blank=True, null=True)
    activa = models.BooleanField(
        default=True,
        help_text="Marcar como inactiva para evitar envíos"
    )
    enviada = models.BooleanField(
        default=False,
        verbose_name="¿Enviada?",
        help_text="Se marca automáticamente al enviar"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha real de envío masivo"
    )

    class Meta:
        ordering = ['-fecha_creacion']  
        verbose_name_plural = "Divulgaciones"

    def __str__(self):
        return f"Divulgación #{self.id_divulgacion} (Creada: {self.fecha_creacion.date()})"

class LogEnvioEmail(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    divulgacion = models.ForeignKey(Divulgacion, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    exito = models.BooleanField(default=False)
    error = models.CharField(max_length=200, blank=True, null=True)
    direccion_email = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['usuario', 'divulgacion']),
        ]
        verbose_name = "Log de envío"
        verbose_name_plural = "Logs de envíos"

class LogDescargaJSON(models.Model):
    id_log = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    cesfam = models.ForeignKey('usuario.Cesfam', on_delete=models.SET_NULL, null=True)
    fecha_descarga = models.DateTimeField(auto_now_add=True)
    cantidad_horas = models.IntegerField()
    nombre_archivo = models.CharField(max_length=255)

    def __str__(self):
        return f"Descarga {self.id_log} - {self.usuario} - {self.fecha_descarga}"
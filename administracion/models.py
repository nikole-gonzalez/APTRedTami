from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class PerfilUsuario(models.Model):
    id_perfil = models.AutoField(primary_key=True, verbose_name="Id Perfil")
    telefono = models.IntegerField(default=0)
    cod_acceso = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    usuario_sist = models.OneToOneField('Usuario', on_delete=models.CASCADE)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[('administrador', 'Administrador'), ('paciente', 'Paciente')],
        default='paciente'
    )

    def __str__(self):
        return f"{self.user.username} - {self.usuario_sist.rut_usuario}"

class Usuario(models.Model):
    id_manychat = models.CharField(primary_key=True, max_length=20, verbose_name="Id Manychat")
    rut_usuario = models.IntegerField()
    dv_rut = models.CharField(max_length=1)
    fecha_nacimiento = models.DateTimeField()
    num_whatsapp = models.BigIntegerField()
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cod_comuna = models.ForeignKey('Comuna', on_delete=models.CASCADE)
    email = models.CharField(max_length=255, blank=True)
    cesfam_usuario = models.ForeignKey('usuario.Cesfam', on_delete=models.CASCADE, null = True, blank= True)

    def __str__(self):
        return f"Usuario: {self.rut_usuario}-{self.dv_rut} ({self.id_manychat})"

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
    fecha_envio = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f"Divulgación #{self.id_divulgacion} ({self.fecha_envio})"



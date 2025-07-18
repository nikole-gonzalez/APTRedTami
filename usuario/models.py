from django.db import models
from administracion.models import Usuario
from administracion.models import Comuna

class Agenda(models.Model):
    id_agenda = models.AutoField(primary_key=True)
    fecha_atencion = models.DateField()
    hora_atencion = models.TimeField()
    requisito_examen = models.CharField(max_length=200)
    id_cesfam = models.ForeignKey('Cesfam', on_delete=models.CASCADE)
    id_manychat = models.ForeignKey('administracion.Usuario', on_delete=models.CASCADE)
    id_procedimiento = models.ForeignKey('TipoProcedimiento', on_delete=models.CASCADE)

    def __str__(self):
        return f"Agenda #{self.id_agenda} - {self.fecha_atencion.strftime('%d/%m/%Y')} {self.hora_atencion}"

class Cesfam(models.Model):
    id_cesfam = models.AutoField(primary_key=True)
    nombre_cesfam = models.CharField(max_length=200)
    telefono_cesfam = models.CharField(max_length=15)
    cod_comuna = models.ForeignKey('administracion.Comuna', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre_cesfam}"

class CodigoFonasa(models.Model):
    cod_fonasa = models.BigIntegerField(primary_key=True)
    nombre_prestacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.cod_fonasa} - {self.nombre_prestacion}"

class CodigoSnomed(models.Model):
    cod_snomed = models.BigIntegerField(primary_key=True)
    nombre_prestacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.cod_snomed} - {self.nombre_prestacion}"


class TipoProcedimiento(models.Model):
    id_procedimiento = models.AutoField(primary_key=True)
    nombre_procedimiento = models.CharField(max_length=100)
    cod_snomed = models.ForeignKey(CodigoSnomed, on_delete=models.CASCADE)
    cod_fonasa = models.ForeignKey(CodigoFonasa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre_procedimiento})"

class HoraAgenda(models.Model):
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada')
    )

    id_hora = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cesfam = models.ForeignKey('Cesfam', on_delete=models.DO_NOTHING, db_column='id_cesfam')
    estado = models.CharField(max_length=20, choices=ESTADOS)
    id_manychat = models.CharField(max_length=255, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario_horas_agenda'
        managed = False
        indexes = [
            models.Index(fields=['fecha', 'hora'], name='idx_fecha_hora'),
            models.Index(fields=['estado'], name='idx_estado'),
        ]

    def _str_(self):
        return f"{self.fecha} {self.hora} - {self.cesfam} ({self.estado})"


class Recordatorio(models.Model):
    agenda = models.ForeignKey('Agenda', on_delete=models.CASCADE)
    email = models.EmailField() 
    enviado = models.BooleanField(default=False)
    fecha_programada = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recordatorios_programados' 

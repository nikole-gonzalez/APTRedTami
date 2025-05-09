from django.contrib import admin
from .models import *

class AgendaAdmin(admin.ModelAdmin):
    list_display=("id_agenda", "fecha_atencion", "hora_atencion", "requisito_examen", "id_cesfam", "id_manychat", "id_procedimiento")
    search_fields=("id_agenda", "fecha_atencion", "hora_atencion", "requisito_examen", "id_cesfam", "id_manychat", "id_procedimiento")
    list_filter=("id_agenda", "fecha_atencion", "hora_atencion", "requisito_examen", "id_cesfam", "id_manychat", "id_procedimiento")

class CesfamAdmin(admin.ModelAdmin):
    list_display=("id_cesfam", "nombre_cesfam", "telefono_cesfam", "cod_comuna")
    search_fields=("id_cesfam", "nombre_cesfam", "telefono_cesfam", "cod_comuna")
    list_filter=("id_cesfam", "nombre_cesfam", "telefono_cesfam", "cod_comuna")

class CodigoFonasaAdmin(admin.ModelAdmin):
    list_display=("cod_fonasa","nombre_prestacion")
    search_fields=("cod_fonasa","nombre_prestacion")
    list_filter=("cod_fonasa","nombre_prestacion")

class CodigoSnomedAdmin(admin.ModelAdmin):
    list_display=("cod_snomed","nombre_prestacion")
    search_fields=("cod_snomed","nombre_prestacion")
    list_filter=("cod_snomed","nombre_prestacion")

class TipoProcedimientoAdmin(admin.ModelAdmin):
    list_display=("id_procedimiento","nombre_procedimiento","cod_snomed","cod_fonasa")
    search_fields=("id_procedimiento","nombre_procedimiento","cod_snomed","cod_fonasa")
    list_filter=("id_procedimiento","nombre_procedimiento","cod_snomed","cod_fonasa")

admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Cesfam, CesfamAdmin)
admin.site.register(CodigoFonasa, CodigoFonasaAdmin)
admin.site.register(CodigoSnomed, CodigoSnomedAdmin)
admin.site.register(TipoProcedimiento, TipoProcedimientoAdmin)
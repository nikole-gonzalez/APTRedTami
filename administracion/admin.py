from django.contrib import admin
from .models import *

class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display=("id_perfil", "telefono", "cod_acceso", "fecha_creacion", "user", "usuario_sist","tipo_usuario")
    search_fields=("id_perfil", "telefono", "cod_acceso", "fecha_creacion", "user", "usuario_sist","tipo_usuario")
    list_filter=("id_perfil", "telefono", "cod_acceso", "fecha_creacion", "user", "usuario_sist", "tipo_usuario")
    
class UsuarioAdmin(admin.ModelAdmin):
    list_display=("id_manychat","rut_usuario","dv_rut","fecha_nacimiento","num_whatsapp","fecha_ingreso","cod_comuna", "email", "cesfam_usuario")
    search_fields=("id_manychat","rut_usuario","dv_rut","fecha_nacimiento","num_whatsapp","fecha_ingreso","cod_comuna", "email", "cesfam_usuario")
    list_filter=("id_manychat","rut_usuario","dv_rut","fecha_nacimiento","num_whatsapp","fecha_ingreso","cod_comuna", "email", "cesfam_usuario")

class RegionAdmin(admin.ModelAdmin):
    list_display=("cod_region","nombre_region")
    search_fields=("cod_region","nombre_region")
    list_filter=("cod_region","nombre_region")

class ProvinciaAdmin(admin.ModelAdmin):
    list_display=("cod_provincia","nombre_provincia","cod_region")
    search_fields=("cod_provincia","nombre_provincia","cod_region")
    list_filter=("cod_provincia","nombre_provincia","cod_region")

class ComunaAdmin(admin.ModelAdmin):
    list_display=("cod_comuna","nombre_comuna","cod_provincia")
    search_fields=("cod_comuna","nombre_comuna","cod_provincia")
    list_filter=("cod_comuna","nombre_comuna","cod_provincia")

class UsuarioTextoPreguntaAdmin(admin.ModelAdmin):
    list_display=("id_texto_preg","texto_pregunta","fecha_pregunta_texto","id_manychat")
    search_fields=("id_texto_preg","texto_pregunta","fecha_pregunta_texto","id_manychat")
    list_filter=("id_texto_preg","texto_pregunta","fecha_pregunta_texto","id_manychat")

class PregTMAdmin(admin.ModelAdmin):
    preg_tm = models.CharField(max_length=200)
    list_display=("id_preg_tm","preg_tm","cod_pregunta_tm")
    search_fields=("id_preg_tm","preg_tm","cod_pregunta_tm")
    list_filter=("id_preg_tm","preg_tm","cod_pregunta_tm")

class OpcTMAdmin(admin.ModelAdmin):
    list_display=("id_opc_tm","opc_resp_tm","id_preg_tm")
    search_fields=("id_opc_tm","opc_resp_tm","id_preg_tm")
    list_filter=("id_opc_tm","opc_resp_tm","id_preg_tm")

class RespTMAdmin(admin.ModelAdmin):
    list_display=("id_resp_tm","fecha_respuesta_tm","id_opc_tm","id_manychat")
    search_fields=("id_resp_tm","fecha_respuesta_tm","id_opc_tm","id_manychat")
    list_filter=("id_resp_tm","fecha_respuesta_tm","id_opc_tm","id_manychat")

class PregDSAdmin(admin.ModelAdmin):
    list_display=("id_preg_ds","preg_ds","cod_pregunta_ds")
    search_fields=("id_preg_ds","preg_ds","cod_pregunta_ds")
    list_filter=("id_preg_ds","preg_ds","cod_pregunta_ds")

class OpcDSAdmin(admin.ModelAdmin):
    list_display=("id_opc_ds","opc_resp_ds","id_preg_ds")
    search_fields=("id_opc_ds","opc_resp_ds","id_preg_ds")
    list_filter=("id_opc_ds","opc_resp_ds","id_preg_ds")

class RespDSAdmin(admin.ModelAdmin):
    list_display=("id_resp_ds","fecha_respuesta_ds","id_opc_ds","id_manychat")
    search_fields=("id_resp_ds","fecha_respuesta_ds","id_opc_ds","id_manychat")
    list_filter=("id_resp_ds","fecha_respuesta_ds","id_opc_ds","id_manychat")

class PregFRMAdmin(admin.ModelAdmin):
    list_display=("id_preg_frm","preg_frm","cod_pregunta_frm")
    search_fields=("id_preg_frm","preg_frm","cod_pregunta_frm")
    list_filter=("id_preg_frm","preg_frm","cod_pregunta_frm")

class OpcFRMAdmin(admin.ModelAdmin):
    list_display=("id_opc_frm","opc_resp_frm","id_preg_frm")
    search_fields=("id_opc_frm","opc_resp_frm","id_preg_frm")
    list_filter=("id_opc_frm","opc_resp_frm","id_preg_frm")   

class RespFRMAdmin(admin.ModelAdmin):
    list_display=("id_resp_frm","fecha_respuesta_frm","id_opc_frm","id_manychat")
    search_fields=("id_resp_frm","fecha_respuesta_frm","id_opc_frm","id_manychat")
    list_filter=("id_resp_frm","fecha_respuesta_frm","id_opc_frm","id_manychat")

class PregFRNMAdmin(admin.ModelAdmin):
    list_display=("id_preg_frnm","preg_frnm","cod_pregunta_frnm")
    search_fields=("id_preg_frnm","preg_frnm","cod_pregunta_frnm")
    list_filter=("id_preg_frnm","preg_frnm","cod_pregunta_frnm")

class OpcFRNMAdmin(admin.ModelAdmin):
    list_display=("id_opc_frnm","opc_resp_frnm","id_preg_frnm")
    search_fields=("id_opc_frnm","opc_resp_frnm","id_preg_frnm")
    list_filter=("id_opc_frnm","opc_resp_frnm","id_preg_frnm")

class RespFRNMAdmin(admin.ModelAdmin):
    list_display=("id_resp_frnm","fecha_respuesta_frnm","id_opc_frnm","id_manychat")
    search_fields=("id_resp_frnm","fecha_respuesta_frnm","id_opc_frnm","id_manychat")
    list_filter=("id_resp_frnm","fecha_respuesta_frnm","id_opc_frnm","id_manychat")

class DivulgacionAdmin(admin.ModelAdmin):
    list_display=("id_divulgacion","texto_divulgacion","url","fecha_envio","imagen")
    search_fields=("id_divulgacion","texto_divulgacion","url","fecha_envio","imagen")
    list_filter=("id_divulgacion","texto_divulgacion","url","fecha_envio","imagen")

admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Comuna, ComunaAdmin)
admin.site.register(UsuarioTextoPregunta, UsuarioTextoPreguntaAdmin)
admin.site.register(PregTM, PregTMAdmin)
admin.site.register(OpcTM, OpcTMAdmin)
admin.site.register(RespTM, RespTMAdmin)
admin.site.register(PregDS, PregDSAdmin)
admin.site.register(OpcDS, OpcDSAdmin)
admin.site.register(RespDS, RespDSAdmin)
admin.site.register(PregFRM, PregFRMAdmin)
admin.site.register(OpcFRM, OpcFRMAdmin)
admin.site.register(RespFRM, RespFRMAdmin)
admin.site.register(PregFRNM, PregFRNMAdmin)
admin.site.register(OpcFRNM, OpcFRNMAdmin)
admin.site.register(RespFRNM, RespFRNMAdmin)
admin.site.register(Divulgacion, DivulgacionAdmin)
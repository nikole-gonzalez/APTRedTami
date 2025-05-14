from administracion.models import (
    RespTM, RespDS, RespFRM, RespFRNM
)

def verificar_tipo_completo(usuario, tipo):
    if tipo == 'TM':
        return RespTM.objects.filter(id_manychat=usuario).exists()
    elif tipo == 'DS':
        return RespDS.objects.filter(id_manychat=usuario).exists()
    elif tipo == 'FRM':
        return RespFRM.objects.filter(id_manychat=usuario).exists()
    elif tipo == 'FRNM':
        return RespFRNM.objects.filter(id_manychat=usuario).exists()
    return False

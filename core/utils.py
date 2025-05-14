from django.core.cache import cache
from administracion.models import RespTM, RespDS, RespFRM, RespFRNM

def verificar_cuestionario_completo(id_manychat):
    """
    Verifica si el usuario ha respondido todas las preguntas requeridas
    según los tipos de cuestionario.
    
    Args:
        id_manychat (str): ID del usuario en ManyChat
        
    Returns:
        bool: True si completó todos los cuestionarios requeridos
    """

    REQUISITOS = {
        'TM': 6,  
        'DS': 3,   
        'FRM': 4,  
        'FRNM': 5 
    }
    
    cache_key = f'quiz_complete_{id_manychat}'

    if cached_result := cache.get(cache_key):
        return cached_result
    
    conteo_respuestas = {
        'TM': RespTM.objects.filter(id_manychat=id_manychat).count(),
        'DS': RespDS.objects.filter(id_manychat=id_manychat).count(),
        'FRM': RespFRM.objects.filter(id_manychat=id_manychat).count(),
        'FRNM': RespFRNM.objects.filter(id_manychat=id_manychat).count()
    }
    
    cuestionario_completo = all(
        conteo_respuestas[tipo] >= cantidad
        for tipo, cantidad in REQUISITOS.items()
    )
    
    cache.set(cache_key, cuestionario_completo, 1800)
    
    return cuestionario_completo
import re

def validar_rut_chileno(rut):
    rut = rut.strip().upper()

    rut_limpio = re.sub(r'[\.\s]', '', rut)

    if not re.match(r'^\d{1,8}-?[\dK]$', rut_limpio):
        return None

    if '-' in rut_limpio:
        numero, dv = rut_limpio.split('-')
    else:
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]

    try:
        numero = int(numero)
    except ValueError:
        return None
    
    suma = 0
    multiplicador = 2
    
    for d in reversed(str(numero)):
        suma += int(d) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_esperado = str(11 - resto) if resto != 0 else '0'
    dv_esperado = 'K' if dv_esperado == '10' else dv_esperado
    
    if dv != dv_esperado:
        return None
    
    return f"{numero}-{dv}" 
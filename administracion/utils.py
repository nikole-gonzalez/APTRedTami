from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

#Función para paginación
def paginacion_queryset1(request, queryset, items_por_pagina=20):
    paginator = Paginator(queryset, items_por_pagina)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj

def paginacion_lista2(request, lista, items_por_pagina=20):
    paginator = Paginator(lista, items_por_pagina)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj

key = settings.ENCRYPT_KEY.encode() 
cipher_suite = Fernet(key)

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data) -> str | None:
    try:
        if isinstance(encrypted_data, bytes):
            decrypted = cipher_suite.decrypt(encrypted_data)
        else:
            decrypted = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except InvalidToken:
        return None
    except Exception:
        return None
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
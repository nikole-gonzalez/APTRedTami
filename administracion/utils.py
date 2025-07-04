from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat

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

def filtrar_por_rut_o_manychat(queryset, query):
    if not query:
        return queryset

    cleaned_query = query.replace(".", "").replace("-", "").replace(" ", "").lower()

    queryset = queryset.annotate(
        manychat_rut_completo=Concat(
            F('id_manychat__rut_usuario'),
            Value('-'),
            F('id_manychat__dv_rut'),
            output_field=CharField()
        ),
        manychat_rut_sin_formato=Concat(
            F('id_manychat__rut_usuario'),
            F('id_manychat__dv_rut'),
            output_field=CharField()
        )
    )

    filtros = Q(manychat_rut_completo__icontains=query) | Q(manychat_rut_sin_formato__icontains=cleaned_query)

    if len(cleaned_query) > 1:
        filtros |= Q(id_manychat__rut_usuario__icontains=cleaned_query[:-1])

    filtros |= Q(id_manychat__id_manychat__icontains=query)

    return queryset.filter(filtros)

def filtro_listado_priorizado(queryset, query):
    if not query:
        return queryset

    cleaned_query = query.replace(".", "").replace("-", "").replace(" ", "").lower()

    queryset = queryset.annotate(
        rut_completo=Concat(
            F('rut_usuario'),
            Value('-'),
            F('dv_rut'),
            output_field=CharField()
        ),
        rut_sin_formato=Concat(
            F('rut_usuario'),
            F('dv_rut'),
            output_field=CharField()
        )
    )

    filtros = Q(rut_completo__icontains=query) | Q(rut_sin_formato__icontains=cleaned_query)

    if len(cleaned_query) > 1:
        filtros |= Q(rut_usuario__icontains=cleaned_query[:-1])

    filtros |= Q(id_manychat__icontains=query)

    return queryset.filter(filtros)
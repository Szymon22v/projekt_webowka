from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def paginuj(queryset, request, domyslna_na_strone=10):
    DOZWOLONE = [5, 10, 25, 50, 100]
    try:
        na_strone = int(request.GET.get('na_strone', domyslna_na_strone))
        if na_strone not in DOZWOLONE:
            na_strone = domyslna_na_strone
    except (ValueError, TypeError):
        na_strone = domyslna_na_strone

    paginator = Paginator(queryset, na_strone)
    numer = request.GET.get('strona', 1)
    try:
        strona = paginator.page(numer)
    except PageNotAnInteger:
        strona = paginator.page(1)
    except EmptyPage:
        strona = paginator.page(paginator.num_pages)
    return strona, na_strone


def zachowaj_parametry_get(request, wykluczenia=None):
    if wykluczenia is None:
        wykluczenia = ['strona', 'na_strone']
    params = request.GET.copy()
    for k in wykluczenia:
        params.pop(k, None)
    return params.urlencode()

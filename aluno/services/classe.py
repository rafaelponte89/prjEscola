from django.template.loader import render_to_string

def renderizarTabela(classes_por_serie, request):
    return render_to_string(
        'aluno/classe/partials/tabela_classes.html',
        {
            'classes_por_serie': dict(classes_por_serie),
        },
        request=request
    )



from django.template.loader import render_to_string

def renderizarTabela(classes, request):
    html = render_to_string(
            'aluno/classe/partials/tabela_classes.html',
            {
                'classes': classes,
            },
            request=request
        )
    return html

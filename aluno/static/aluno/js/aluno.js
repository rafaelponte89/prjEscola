

function buscarAluno(rm) {
    const url = $("#urls").data("buscar-aluno");

    $.post(url,
        {
            rm: rm,
        }).done((html) => {
            $("#dadosAluno").html(html);

            // Fecha qualquer modal ativo primeiro
            $('.modal').modal('hide');

            // Remove qualquer backdrop restante
            $('.modal-backdrop').remove();

            // Abre o modal
            const modalEl = document.getElementById("atualizarModal");
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
}


//Cancelar RM
function sendCancelar(rm) {
    const url = $("#urls").data("cancelar-rm");

    $.post({
        url: url,

        headers: {
        },
        data: {
            rm: rm,
        },
        success: (response) => {
            configurarElementos(response);
        },
        fail: (response) => { },
    });
}

//Buscar Aluno por rm para cancelar
function buscarAlunoCancelar(rm) {
    const url = $("#urls").data("buscar-cancelar");

    $.post({
        url: url,

        headers: {
        },
        data: {
            rm: rm,
        },
        success: (response) => {
            $("#identificador").html(response);
        },
        fail: (response) => { },
    });
}

// Recarregar Tabela Estado Inicial
function recarregarTabela() {
    const url = $("#urls").data("recarregar-tabela");

    $.get({
        url: url,
        success: (response) => {
            $("#corpoTabela").html(response.html);
        },
        fail: (response) => { },
    });
}

// Pesquisar por nome
function sendBuscar() {
    let nome = document.getElementById("id_nome").value;
    let filtro = localStorage.getItem("filtro");
    const url = $("#urls").data("pesquisar-aluno");


    $.post({
        url: url,
        data: {
            nome: nome,
            filtro: filtro,
        },
        headers: {
        },
        success: (response) => {
            // Atualiza o corpo da tabela
            $("#corpoTabela").html(response.html);

            // Mostra ou esconde a mensagem
            if (response.mensagem) {
                $("#corpoTabela").html(response.mensagem).show();
            } else {
                $("#mensagemTabelaAluno").hide();
            }
        },
    });
}


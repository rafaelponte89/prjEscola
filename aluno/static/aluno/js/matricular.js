
function exibirTelaMatricula(classe) {
    $.get({
        url: "telamatricular",
        data: {
            classe: classe,
        },
        success: (response) => {
            $("#nomeAluno").off("keyup");
            $("#dadosMatricula").html(response);
            $("#nomeAluno").keyup(() => sendBuscar());
        },
        fail: (response) => {
            alert("Erro na matricula");
        },
    });
}

function sendBuscar() {
    let nome = document.getElementById("nomeAluno").value;
    let ano = $("#anoConfig").val();

    $.get({
        url: "buscarAluno",
        data: {
            nome: nome,
            ano: ano,
        },
        success: (response) => {
            $("#tabelaAlunos").html(response);
            $(".adicionarNaClasse").off("click");
            $(".adicionarNaClasse").click(function () {
                aluno = $(this).val();
                adicionarNaClasse(aluno);
                $(this).addClass("disabled");
            });
        },
    });
}

function adicionarNaClasse(aluno) {
    console.log($("#dataMatricula").val());
    $.get({
        url: "adicionarNaClasse",
        data: {
            ano: $("#ano").html(),
            classe: $("#codClasseMatricula").val(),
            aluno: aluno,
            data_matricula: $("#dataMatricula").val(),
        },
        success: (response) => {
            $("#mensagensModal").html(response);
            setTimeout(function () {
                $("#mensagemModal").css("display", "none");
            }, 3000);
        },
        fail: (response) => { },
    });
}



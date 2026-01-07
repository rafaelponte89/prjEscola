
function inicializarMatriculas(urls) {
  $(document).ready(() => {
    // --- 1. CONFIGURAÇÕES E TOKENS ---


    // Função utilitária para mensagens
    function notificar(msg) {
      $("#mensagens").html(msg).stop(true, true).show();
      setTimeout(() => $("#mensagens").fadeOut(), 3000);
    }

    function notificarModal(msg) {
      $("#mensagensModal").html(msg).stop(true, true).show();
      setTimeout(() => $("#mensagensModal").fadeOut(), 3000);
    }

    // Função utilitária para data atual (YYYY-MM-DD)
    function retornarDataHoje() {
      return new Date().toISOString().slice(0, 10);
    }

    // --- 2. DELEGAÇÃO DE EVENTOS (DELEGATE) ---
    // Registrados uma única vez. Funcionam para elementos estáticos e dinâmicos.

    // Botões da Tabela (Excluir e Movimentar)
    $("#corpoTabela").on("click", ".excluir", function () {
      const id = $(this).val();

      excluirMatricula(id);

    });

    $("#corpoTabela").on("click", ".movimentar", function () {
      buscarMatricula($(this).val());
    });

    // Botão de Matricular (Abre Modal)
    $(document).on("click", ".matricular", function () {
      const classe = $("#classes").val();
      exibirTelaMatricula(classe);
    });

    // Botão Adicionar Aluno (Dentro do Modal de Busca)
    $(document).on("click", ".adicionarNaClasse", function () {
      const btn = $(this);
      const alunoId = btn.val();
      btn.addClass("disabled");
      adicionarNaClasse(alunoId);
    });

    // --- 3. LÓGICA DE BUSCA COM DEBOUNCE ---
    let timerBusca;
    $(document).on("keyup", "#pesquisaAluno", function () {
      const termo = $(this).val();
      clearTimeout(timerBusca);
      timerBusca = setTimeout(() => {
        sendBuscar(termo, localStorage.getItem("idAno"));
      }, 300);
    });

    // --- 4. FUNÇÕES AJAX (LÓGICA DE NEGÓCIO) ---

    function carregarMatriculas(classe) {
      if (!classe) return;
      $.get(urls.carregar_matriculas, { classe: classe })
        .done((response) => $("#corpoTabela").html(response));
    }

    function excluirMatricula(matricula) {
      $.get(urls.excluir_matricula, { matricula: matricula })
        .done((response) => {
          notificar(response);
          carregarMatriculas($("#classes").val());
        });
    }

    function adicionarNaClasse(aluno) {
      $.get({
        url: urls.adicionar_na_classe,
        data: {
          ano: localStorage.getItem("idAno"),
          classe: $("#codClasseMatricula").val(),
          aluno: aluno,
          data_matricula: $("#dataMatriculaIndividual").val(),
        }
      }).done((response) => {
        notificarModal(response);
        carregarMatriculas($("#classes").val());
      });
    }

    function sendBuscar(nomeAluno, ano) {
      $.get(urls.buscar_aluno, { nome: nomeAluno, ano: ano })
        .done((response) => $("#tabelaAlunos").html(response));
    }

    /*function carregarClasses(ano) {
      $.get(urls.carregar_classes, { ano: ano })
        .done((response) => {
          $("#classes").html(response);
          const ultima = localStorage.getItem("ultimaClasse");
          if (ultima) $("#classes").val(ultima);
        });
    }*/

    function ordemAlfabetica(classe) {
      $.get(urls.ordem_alfabetica, { classe: classe })
        .done((response) => $("#corpoTabela").html(response));
    }

    // 2. A Função que faz o AJAX (Certifique-se que o nome é 'exibir')
    function exibirTelaMatricula(classe) {
      $.get(urls.tela_matricular, { classe: classe })
        .done((response) => {
          // Preenche os campos do modal com o que veio do Django
          $("#serie").html(response.serie);
          $("#turma").html(response.turma);
          $("#periodo").html(response.periodo);
          $("#codClasseMatricula").val(response.cod_classe);
        })
        .fail(() => {
          alert("Erro ao carregar dados da matrícula");
        });
    }

    // --- 5. MOVIMENTAÇÃO E REMANEJAMENTO ---

    $("#selecaoClasse").hide();

    function carregarMovimentacao() {
      $.get(urls.carregar_movimentacao, (response) => {
        $("#selecaoMovimentacao").html(response);
      });
    }

    $("#selecaoMovimentacao").change(function () {
      if ($(this).val() === "REMA") {
        $("#selecaoClasse").show();
        const ano = localStorage.getItem("idAno");
        const serie = $("#classes").val();
        $.get(urls.carregar_remanejamento, { ano, serie })
          .done((res) => $("#classesRemanejamento").html(res));
      } else {
        $("#selecaoClasse").hide();
      }
    });

    function sendMovimentar(matricula) {
      $.get(urls.movimentar, {
        matricula: matricula,
        data_movimentacao: $("#dataMovimentacao").val(),
        movimentacao: $("#selecaoMovimentacao").val(),
        classe_remanejamento: $("#classesRemanejamento").val(),
        ano: localStorage.getItem("idAno"),
      }).done((response) => {
        notificar(response);

        // Esconde o campo de remanejamento para a próxima vez
        $("#selecaoClasse").hide();

        // Recarrega a tabela
        carregarMatriculas($("#classes").val());

        // CHAMA A DECLARAÇÃO: Pega o RM que foi preenchido no buscarMatricula
        const rm = $("#rmAluno").val();
        sendBaixarDeclaracao(rm);
      });
    }

    function sendBaixarDeclaracao(rm) {
      if (!rm) return;

      $.post({
        url: urls.baixar_declaracao,
        data: {
          rm: rm,
          nome_op: localStorage.getItem("nomeOperador"),
          cargo_op: localStorage.getItem("cargoOperador"),
          rg_op: localStorage.getItem("rgOperador"),
        },
        xhrFields: {
          responseType: 'blob' // Essencial para lidar com arquivos binários (PDF)
        },
        success: (response) => {
          const blob = new Blob([response], { type: "application/pdf" });
          const fileURL = URL.createObjectURL(blob);

          // Abre em uma nova aba
          const newWin = window.open(fileURL);
          if (!newWin) {
            alert("Por favor, permita pop-ups para visualizar a declaração.");
          }
        },
        error: () => alert("Erro ao gerar a declaração em PDF.")
      });
    }

    function buscarMatricula(matricula) {
      $.get(urls.buscar_matricula, { matricula: matricula })
        .done((response) => {
          $("#rmAluno").val(response.rm_aluno);
          $("#nomeAluno").val(response.nome_aluno);
          $("#dataMovimentacao").val(response.data_movimentacao);
          $("#matricula").val(response.id_matricula);

          $("#simMovimentar").off("click").on("click", () => sendMovimentar(matricula));
        });
    }

    // --- 6. UPLOAD DE PDF ---

    $("#arquivoCSV").on("change", function () {
      $("#uploadMatriculas, #dataMatricula").prop("hidden", false).val(retornarDataHoje());
    });

    $("#uploadMatriculas").click(function (e) {
      e.preventDefault();
      const formData = new FormData();
      formData.append("arquivo", $("#arquivoCSV")[0].files[0]);
      formData.append("classe", $("#classes").val());
      formData.append("ano", localStorage.getItem("idAno"));
      formData.append("data_matricula", $("#dataMatricula").val());

      $.ajax({
        url: urls.upload_matriculas,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: (response) => {
          $("#corpoTabela").html(response.html);
          notificar(response.mensagem);
          $("#arquivoCSV").val("");

          // 3. Oculta os botões novamente
          $("#uploadMatriculas").prop("hidden", true);
          $("#dataMatricula").prop("hidden", true);
        }
      });
    });

    // --- 7. INICIALIZAÇÃO FINAL ---
    $("#dataMatriculaIndividual").val(retornarDataHoje());
    carregarMovimentacao();
    //carregarClasses(localStorage.getItem("idAno"));

    $("#classes").change(function () {
      const val = $(this).val();
      localStorage.setItem('ultimaClasse', val);
      carregarMatriculas(val);
    });

    $("#alfabetica").click(() => ordemAlfabetica($("#classes").val()));

    if (localStorage.getItem("ultimaClasse")) {
      carregarMatriculas(localStorage.getItem("ultimaClasse"));
    }

    function exibirHistoricoMatriculas(rm) {
      $.post({
        url: "{% url 'buscarHistoricoMatriculas' %}",

        headers: {
          "X-CSRFToken": csrftoken,
        },
        data: {
          rm: rm,
        },
        success: (response) => {
          $("#dados").html(response);
        },
        fail: (response) => { },
      });
    }

  });

}



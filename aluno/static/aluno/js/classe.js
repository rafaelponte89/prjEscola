window.Classes = {
  inicializarClasses(URLS) {

    $(document).ready(() => {

      function notificar(response) {
        $("#mensagens").html(response);
        setTimeout(function () {
          $("#mensagem").css("display", "none");
        }, 3000);
      }

      function exibirClasse(classe) {
        $.get({
          url: URLS.exibir_classe,
          data: {
            classe: classe,
          },
          success: (response) => {
            console.log(response);
            $("#alunosClasse").html(response.html);
            $("#serie").text(response.serie);
            $("#turma").text(response.turma);
            $("#periodo").text(response.periodo);

          },

          fail: (response) => { },
        });
      }

      // buscar classe
      function buscarClasse(classe) {
        $.get({
          url: URLS.buscar_classe,
          data: {
            classe: classe,
          },
          success: (response) => {

            $("#dadosClasse").html(response);


          },
          fail: (response) => { },
        });
      }

      function sendDeletar() {
        $.post({
          url: URLS.deletar_classe,
          data: {
            classe: $("#codClasse").val(),
          },
          success: (response) => {
            notificar(response);
            sendListar();
          },
          fail: (response) => {
            $("#mensagens").html(response);
          },
        });
      }

      function sendAtualizar() {
        $.post({
          url: URLS.atualizar_classe,
          data: {
            ano: localStorage.getItem("idAno"),
            classe: $("#codClasse").val(),
            serie: $("#id_serie").val(),
            turma: $("#id_turma").val(),
            periodo: $("#id_periodo").val(),
          },
          success: (response) => {
            notificar(response);
            sendListar();
          },
          fail: (response) => {
            $("#mensagens").html(response);
          },
        });
      }

      function sendGravar() {
        $.post({
          url: URLS.gravar_classe,
          data: {
            ano: localStorage.getItem("idAno"),
            serie: $("#serie").val(),
            turma: $("#turma").val().toUpperCase(),
            periodo: $("#periodo").val(),
          },
          success: (response) => {
            notificar(response);

            sendListar();
          },
          fail: (response) => { },
        });
      }

      function sendListar() {
        $.get({
          url: URLS.listar_classe,
          data: {
            ano: localStorage.getItem("idAno"),
          },
          success: (response) => {

            $("#corpoTabela").html(response.html);
          },
          fail: (response) => { },
        });
      }

      $("#abrirQuadro").click(() => {
        exibirQuadro();
      });

      $("#salvarConfig").click(() => {
        sendListar();
      });

      sendListar();

      function limparCampos() {
        $("#serie").val("");
        $("#turma").val("");
        $("#periodo").val("");
      }

      function exibirQuadro() {
        $.get({
          url: URLS.exibir_quadro,
          data: {
            ano: localStorage.getItem("idAno"),
          },
          success: (response) => {
            $("#quadroClasse").html(response);
          },
          fail: () => { },
        });
      }

      function gerarTurmas() {
        $.post({
          url: URLS.gerar_turmas,
          data: {
            ano: localStorage.getItem("idAno"),
            m1: $("#m1").val(),
            m2: $("#m2").val(),
            m3: $("#m3").val(),
            m4: $("#m4").val(),
            m5: $("#m5").val(),
            m6: $("#m6").val(),
            m7: $("#m7").val(),
            m8: $("#m8").val(),
            m9: $("#m9").val(),
            t1: $("#t1").val(),
            t2: $("#t2").val(),
            t3: $("#t3").val(),
            t4: $("#t4").val(),
            t5: $("#t5").val(),
            t6: $("#t6").val(),
            t7: $("#t7").val(),
            t8: $("#t8").val(),
            t9: $("#t9").val(),
            i1: $("#i1").val(),
            i2: $("#i2").val(),
            i3: $("#i3").val(),
            i4: $("#i4").val(),
            i5: $("#i5").val(),
            i6: $("#i6").val(),
            i7: $("#i7").val(),
            i8: $("#i8").val(),
            i9: $("#i9").val(),

          },
          success: (response) => {
            sendListar();
          },
        });
      }

      // Delegação fixar no elemento mais proximo que não será reconstruído assim o evento permanece
      $("#corpoTabela").on("click", ".atualizar", function () {
        classe = $(this).data("id");
        buscarClasse(classe);
      });

      $("#corpoTabela").on("click", ".visualizar", function () {
        classe = $(this).data("id")
        exibirClasse(classe);
      });

      $("#conteudo").on("click", "#simAtualizar", function () {
        sendAtualizar();
      });
      $("#conteudo").on("click", "#simDeletar", function () {
        sendDeletar();
      });

      $("#conteudo").on("click", "#gerarTurmas", function () {
        gerarTurmas();
        sendListar();
      });

      $("#painelClasse").on("click", "#gravar", () => {
        sendGravar();
        sendListar();
        limparCampos();
      });

      $("#configuracoesModal").on("hidden.bs.modal", function (e) {
        sendListar();
      });

    });
  }
}
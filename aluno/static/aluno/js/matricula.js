window.Matriculas = {
  urls: {},
  paginaAtual: 1,

  /* ===============================
   * INIT
   * =============================== */
  init(urls) {
    this.urls = urls;

    $(document).ready(() => {
      this.bindEvents();
      this.inicializar();
    });
  },

  /* ===============================
   * UTILIDADES
   * =============================== */
  notificar(html) {
    $("#mensagens").html(html).stop(true, true).show();
    setTimeout(() => $("#mensagens").fadeOut(), 3000);
  },

  notificarModal(html) {
    $("#mensagensModal").html(html).stop(true, true).show();
    setTimeout(() => $("#mensagensModal").fadeOut(), 3000);
  },

  dataHoje() {
    return new Date().toISOString().slice(0, 10);
  },

  getAno() {
    return localStorage.getItem("idAno");
  },

  /* ===============================
   * MATRÍCULAS / TABELA
   * =============================== */
  carregarMatriculas(classe, page = null) {
    if (!classe) return;

    // se page vier, atualiza estado
    if (page !== null) {
      this.paginaAtual = page;
    }

    $.get(this.urls.carregar_matriculas, {
      classe,
      page: this.paginaAtual
    }).done((html) => {
      $("#corpoTabela").html(html);
    });
  },

  excluirMatricula(id) {
    $.get(this.urls.excluir_matricula, { matricula: id })
      .done((response) => {
        this.notificar(response);
        this.carregarMatriculas($("#classes").val(), this.paginaAtual);
      });
  },

  ordemAlfabetica(classe, page) {
    if (!classe) return;

    $.get(this.urls.ordem_alfabetica, {
      classe,
      page
    }).done((html) => {
      $("#corpoTabela").html(html);
    });
  },


  /* ===============================
   * TELA DE MATRÍCULA
   * =============================== */
  exibirTelaMatricula(classe) {
    $.get(this.urls.tela_matricular, { classe })
      .done((response) => {
        $("#serie").html(response.serie);
        $("#turma").html(response.turma);
        $("#periodo").html(response.periodo);
        $("#codClasseMatricula").val(response.cod_classe);
      })
      .fail(() => alert("Erro ao carregar dados da matrícula"));
  },

  adicionarNaClasse(alunoId) {
    $.get(this.urls.adicionar_na_classe, {
      ano: this.getAno(),
      classe: $("#codClasseMatricula").val(),
      aluno: alunoId,
      data_matricula: $("#dataMatriculaIndividual").val(),
    }).done((response) => {
      this.notificarModal(response);
      this.carregarMatriculas($("#classes").val(), this.paginaAtual);
    });
  },

  /* ===============================
   * BUSCAS
   * =============================== */
  buscarAluno(nome) {
    $.get(this.urls.buscar_aluno, {
      nome,
      ano: this.getAno(),
    }).done((html) => $("#tabelaAlunos").html(html));
  },

  buscarMatricula(id) {
    $.get(this.urls.buscar_matricula, { matricula: id })
      .done((response) => {
        $("#rmAluno").val(response.rm_aluno);
        $("#nomeAluno").val(response.nome_aluno);
        $("#dataMovimentacao").val(response.data_movimentacao);
        $("#matricula").val(response.id_matricula);

        $("#simMovimentar")
          .off("click")
          .on("click", () => this.sendMovimentar(id));
      });
  },

  /* ===============================
   * MOVIMENTAÇÃO
   * =============================== */
  carregarMovimentacao() {
    $.get(this.urls.carregar_movimentacao)
      .done((html) => $("#selecaoMovimentacao").html(html));
  },

  sendMovimentar(matricula) {
    $.get(this.urls.movimentar, {
      matricula,
      data_movimentacao: $("#dataMovimentacao").val(),
      movimentacao: $("#selecaoMovimentacao").val(),
      classe_remanejamento: $("#classesRemanejamento").val(),
      ano: this.getAno(),
    }).done((response) => {
      this.notificar(response);
      $("#selecaoClasse").hide();
      this.carregarMatriculas($("#classes").val(), this.paginaAtual);

      const rm = $("#rmAluno").val();
      this.baixarDeclaracao(rm);
    });
  },

  baixarDeclaracao(rm) {
    if (!rm) return;

    $.post({
      url: this.urls.baixar_declaracao,
      data: {
        rm,
        nome_op: localStorage.getItem("nomeOperador"),
        cargo_op: localStorage.getItem("cargoOperador"),
        rg_op: localStorage.getItem("rgOperador"),
      },
      xhrFields: { responseType: "blob" },
      success: (response) => {
        const blob = new Blob([response], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        window.open(url) ||
          alert("Permita pop-ups para visualizar a declaração.");
      },
      error: () => alert("Erro ao gerar declaração."),
    });
  },

  /* ===============================
   * UPLOAD
   * =============================== */
  uploadMatriculas() {
    const formData = new FormData();
    formData.append("arquivo", $("#arquivoCSV")[0].files[0]);
    formData.append("classe", $("#classes").val());
    formData.append("ano", this.getAno());
    formData.append("data_matricula", $("#dataMatricula").val());

    $.ajax({
      url: this.urls.upload_matriculas,
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: (response) => {
        $("#corpoTabela").html(response.html);
        this.notificar(response.mensagem);
        $("#arquivoCSV").val("");
        $("#uploadMatriculas, #dataMatricula").prop("hidden", true);
      },
    });
  },

  /* ===============================
   * EVENTOS
   * =============================== */
  bindEvents() {
    const self = this;
    let timerBusca;


    $("#corpoTabela")
      .on("click", ".pagina", function (e) {
        e.preventDefault();
        const page = $(this).data("page");
        const classe = $("#classes").val();
        Matriculas.carregarMatriculas(classe, page);
      })
      .on("click", ".excluir", function () {
        self.excluirMatricula($(this).val());
      })
      .on("click", ".movimentar", function () {
        self.buscarMatricula($(this).val());
      });


    /* $("#corpoTabela")
       .on("click", ".excluir", function () {
         self.excluirMatricula($(this).val());
       })
       .on("click", ".movimentar", function () {
         self.buscarMatricula($(this).val());
       });*/

    $(document)
      .on("click", ".matricular", () =>
        self.exibirTelaMatricula($("#classes").val())
      )
      .on("click", ".adicionarNaClasse", function () {
        $(this).addClass("disabled");
        self.adicionarNaClasse($(this).val());
      })
      .on("keyup", "#pesquisaAluno", function () {
        clearTimeout(timerBusca);
        timerBusca = setTimeout(
          () => self.buscarAluno($(this).val()),
          300
        );
      });


    $("#classes").on("change", function () {
      localStorage.setItem("ultimaClasse", $(this).val());
      self.carregarMatriculas($("#classes").val(), this.paginaAtual);
    });

    $("#alfabetica").on("click", () => {
      const classe = $("#classes").val();
      self.ordemAlfabetica(classe, self.paginaAtual);
    });


    $("#arquivoCSV").on("change", () => {
      $("#uploadMatriculas, #dataMatricula")
        .prop("hidden", false)
        .val(self.dataHoje());
    });

    $("#uploadMatriculas").on("click", (e) => {
      e.preventDefault();
      self.uploadMatriculas();
    });

    $("#selecaoMovimentacao").on("change", function () {
      if ($(this).val() === "REMA") {
        $("#selecaoClasse").show();
        $.get(self.urls.carregar_remanejamento, {
          ano: self.getAno(),
          serie: $("#classes").val(),
        }).done((html) => $("#classesRemanejamento").html(html));
      } else {
        $("#selecaoClasse").hide();
      }
    });
  },

  /* ===============================
   * INICIALIZAÇÃO
   * =============================== */
  inicializar() {
    $("#dataMatriculaIndividual").val(this.dataHoje());
    $("#selecaoClasse").hide();
    this.carregarMovimentacao();

    const ultimaClasse = localStorage.getItem("ultimaClasse");
    if (ultimaClasse) {
      this.carregarMatriculas(ultimaClasse, this.paginaAtual);
    }
  },
};

window.Classes = {
  urls: {},

  init(urls) {
    this.urls = urls;

    $(document).ready(() => {
      this.bindEvents();
      this.listarClasses();
    });
  },

  /* =======================
   * UTILITÁRIOS
   * ======================= */
  getAno() {
    return localStorage.getItem("idAno");
  },

  notificar(html) {
    $("#mensagens").html(html);
    setTimeout(() => $("#mensagem").hide(), 3000);
  },

  /* =======================
   * REQUESTS
   * ======================= */

  listarClasses() {
    $.get(this.urls.listar_classe, {
      ano: this.getAno(),
    }).done((response) => {
      $("#corpoTabela").html(response.html);
    }).fail(() => {
      console.error("Erro ao listar classes");
    });
  },

  carregarClasses(ano) {
    $.get(this.urls.carregar_classe, { ano: ano })
      .done((response) => {
        $("#classes").html(response);

        const ultima = localStorage.getItem("ultimaClasse");
        if (ultima) {
          $("#classes").val(ultima);
        }
      })
      .fail((err) => {
        console.error("Erro ao carregar classes", err);
      });
  },

  buscarClasse(id) {
    $.get(this.urls.buscar_classe, {
      classe: id,
    }).done((html) => {
      $("#dadosClasse").html(html);
    });
  },

  exibirClasse(id) {
    $.get(this.urls.exibir_classe, {
      classe: id,
    }).done((response) => {
      $("#alunosClasse").html(response.html);
      $("#serie").text(response.serie);
      $("#turma").text(response.turma);
      $("#periodo").text(response.periodo);
    });
  },

  /* ✅ MÉTODO QUE ESTAVA FALTANDO */
  exibirQuadro() {
    $.get(this.urls.exibir_quadro, {
      ano: this.getAno(),
    }).done((html) => {
      $("#quadroClasse").html(html);
    });
  },

  gravarClasse() {
    $.post(this.urls.gravar_classe, {
      ano: this.getAno(),
      serie: $("#serie").val(),
      turma: $("#turma").val().toUpperCase(),
      periodo: $("#periodo").val(),
    }).done((response) => {
      this.notificar(response);
      this.listarClasses();
      this.limparCampos();
    });
  },

  atualizarClasse() {
    $.post(this.urls.atualizar_classe, {
      ano: this.getAno(),
      classe: $("#codClasse").val(),
      serie: $("#id_serie").val(),
      turma: $("#id_turma").val(),
      periodo: $("#id_periodo").val(),
    }).done((response) => {
      this.notificar(response);
      this.listarClasses();
    });
  },

  deletarClasse() {
    $.post(this.urls.deletar_classe, {
      classe: $("#codClasse").val(),
    }).done((response) => {
      this.notificar(response);
      this.listarClasses();
    });
  },

  gerarTurmas() {
    if (!document.getElementById("m1")) {
      console.warn("Quadro ainda não carregado");
      return;
    }

    $.post(this.urls.gerar_turmas, {
      ano: this.getAno(),
      ...this.coletarTurmas(),
    }).done(() => {
      this.listarClasses();
      $("#criarQuadroClasseModal").modal("hide");
    });
  },

  coletarTurmas() {
    const dados = {};
    ["m", "t", "i"].forEach((p) => {
      for (let i = 1; i <= 9; i++) {
        const el = document.getElementById(`${p}${i}`);
        dados[`${p}${i}`] = el ? el.value || 0 : 0;
      }
    });
    return dados;
  },

  limparCampos() {
    $("#serie, #turma, #periodo").val("");
  },

  /* =======================
   * EVENTOS
   * ======================= */

  bindEvents() {
    $("#abrirQuadro").on("click", () => this.exibirQuadro());

    $("#painelClasse").on("click", "#gravar", () => this.gravarClasse());

    $("#conteudo").on("click", "#simAtualizar", () => this.atualizarClasse());
    $("#conteudo").on("click", "#simDeletar", () => this.deletarClasse());
    $("#conteudo").on("click", "#gerarTurmas", () => this.gerarTurmas());

    $("#corpoTabela").on("click", ".atualizar", (e) => {
      this.buscarClasse($(e.currentTarget).data("id"));
    });

    $("#corpoTabela").on("click", ".visualizar", (e) => {
      this.exibirClasse($(e.currentTarget).data("id"));
    });

    $("#configuracoesModal").on("hidden.bs.modal", () => {
      this.listarClasses();
    });
  },
};

/* 🔁 Compatibilidade com código antigo */
window.Classes.inicializarClasses = window.Classes.init;

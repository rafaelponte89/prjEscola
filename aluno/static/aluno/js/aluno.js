window.Alunos = {
    urls: {},

    /* ===============================
     * INIT
     * =============================== */
    init(urls) {
        this.urls = urls;

        $(document).ready(() => {
            this.bindEvents();
            this.recarregarTabela();
        });
    },

    /* ===============================
     * UTILIDADES
     * =============================== */
    notificar(html) {
        $("#mensagens").html(html).show();
        setTimeout(() => $("#mensagens").fadeOut(), 3000);
    },

    limparFormulario() {
        $("#cadastrarAluno")[0]?.reset();
        $("#id_nome").focus();
    },

    /* ===============================
     * BUSCAR / ATUALIZAR
     * =============================== */
    buscarAluno(rm) {
        $.post(this.urls.buscar_aluno, { rm })
            .done((html) => {
                $("#dadosAluno").html(html);

                $(".modal").modal("hide");
                $(".modal-backdrop").remove();

                const modal = new bootstrap.Modal(
                    document.getElementById("atualizarModal")
                );
                modal.show();
            });
    },

    buscarAlunoCancelar(rm) {
        $.post(this.urls.buscar_cancelar, { rm })
            .done((response) => {
                $("#registroAluno").text(response.rm);
                $("#nomeAluno").text(response.nome);
            });
    },

    /* ===============================
     * AÇÕES
     * =============================== */
    sendCancelar(rm) {
        $.post(this.urls.cancelar_rm, { rm })
            .done((response) => {
                this.notificar(response.mensagem);
                this.recarregarTabela();
            });
    },

    sendBuscar() {
        const nome = $("#id_nome").val();
        const filtro = localStorage.getItem("filtro");

        $.post(this.urls.pesquisar_aluno, { nome, filtro })
            .done((response) => {
                if (response.mensagem) {
                    $("#corpoTabela").html(response.mensagem);
                } else {
                    $("#corpoTabela").html(response.html);
                }
            });
    },

    /* ===============================
     * TABELA
     * =============================== */
    recarregarTabela() {
        $.get(this.urls.recarregar_tabela)
            .done((response) => {
                $("#corpoTabela").html(response.html);
            });
    },

    /* ===============================
     * EVENTOS
     * =============================== */
    bindEvents() {
        const self = this;

        // Delegação segura para AJAX
        $("#corpoTabela")
            .on("click", ".atualizar", function () {
                self.buscarAluno($(this).val());
            })
            .on("click", ".advertencia", function () {
                self.buscarAlunoCancelar($(this).val());
            })
            .on("click", ".declaracao", function () {
                Relatorios.sendBaixarDeclaracao($(this).val());
            });

        $("#id_nome").on("keyup", () => self.sendBuscar());

        $("#simCancelar").on("click", () => {
            self.sendCancelar($("#registroAluno").text());
        });

        $("#persorelatorio").on("change", function () {
            if ($(this).is(":checked")) {
                $("#personalizavel").prop("hidden", false);
            }
        });

        $("#rmrelatorio, #telrelatorio").on("change", function () {
            if ($(this).is(":checked")) {
                $("#personalizavel").prop("hidden", true);
            }
        });

        $("#baixarpdf").on("click", () => {
            if ($("#rmrelatorio").is(":checked")) {
                Relatorios.sendBaixarPdf($("#id_rmi").val(), $("#id_rmf").val());
            } else if ($("#telrelatorio").is(":checked")) {
                Relatorios.sendBaixarListaTelefonica($("#classes").val());
            } else if ($("#persorelatorio").is(":checked")) {
                Relatorios.sendBaixarListaPersonalizavel($("#classes").val());
            }
        });

        $("#relatorio").on("click", () => {
            if (window.carregarClasses) {
                carregarClasses(localStorage.getItem("idAno"));
            }
        });
    }
};

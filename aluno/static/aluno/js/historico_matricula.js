window.HistoricosMatriculas = {
    urls: {},

    /* ===============================
     * INIT
     * =============================== */
    init(urls) {
        this.urls = urls;

        $(document).ready(() => {
            this.bindEvents();

        });
    },

    bindEvents() {
        const self = this;
        $(document).on("click", ".historico", function () {
            const rm = $(this).data("rm");

            $.post(self.urls.buscar_historico_matricula, { rm })
                .done((response) => {
                    $("#containerModalHistorico").html(response.html);
                    new bootstrap.Modal(
                        document.getElementById(
                            "modalHistoricoMatriculas"
                        )
                    ).show();
                })
                .fail(() =>
                    alert("Erro ao carregar histórico de matrículas.")
                );

        });
    }
}

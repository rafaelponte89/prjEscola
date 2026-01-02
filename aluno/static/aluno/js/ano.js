function inicializarAnos(URLS) {
    $(document).ready(() => {

        function notificar(response) {
            $("#mensagens").html(response);
            setTimeout(function () {
                $("#mensagem").css("display", "none");
            }, 3000);

        }

        function sendGravar(ano) {
            $.get({
                url: URLS.gravar_ano,
                data: {
                    ano: ano
                },
                success: (response) => {
                    notificar(response);
                    sendListarAnos();

                },
                fail: (response) => {

                }
            });

        }

        function sendExcluirAno(ano) {
            $.get({
                url: URLS.excluir_ano,
                data: {
                    ano: ano
                },
                success: (response) => {
                    notificar(response);
                    if ($("#descAno").val() != '') {
                        sendBuscarAno($("#descAno").val());
                    }
                    else {
                        sendListarAnos();
                    }

                },
                fail: (response) => {

                }
            });
        }

        function sendListarAnos() {
            $.get({
                url: URLS.listar_ano,
                data: {},
                success: (response) => {
                    $("#corpoTabela").html(response);

                    recarregarElementos();
                },
                fail: (response) => {

                }

            });
        }

        function sendBuscarAno(ano) {
            $.get({
                url: URLS.buscar_ano,
                data: {
                    ano: ano
                },
                success: (response) => {

                    $("#corpoTabela").html(response);
                    recarregarElementos();

                },
                fail: (response) => {

                }
            });

        }

        function sendFecharAbrirAno(ano) {
            $.get({
                url: URLS.fechar_abrir_ano,
                data: {
                    ano: ano
                },
                success: (response) => {

                    if ($("#descAno").val() != '') {
                        sendBuscarAno($("#descAno").val());
                    }
                    else {
                        sendListarAnos();
                    }
                },
                fail: (response) => {

                }
            });
        }

        function sendSelecionarAno(ano) {
            $.get({
                url: URLS.selecionar_ano,
                data: {
                    ano: ano
                },
                success: (response) => {

                    localStorage.setItem("idAno", response);

                },
                fail: (response) => {
                    alert(response);
                }
            })

        }

        sendListarAnos();

        function recarregarElementos() {
            $(".excluir").off().on("click", function () {
                sendExcluirAno($(this).val());
            });

            $(".status").off().on("click", function () {
                sendFecharAbrirAno($(this).val());
            });

            $("#gravar").off().on("click", function () {
                sendGravar($("#descAno").val());
            });

            $("#buscar").off().on("click", function () {
                sendBuscarAno($("#descAno").val());
            });

            $(".selecionarAno").on('click', function () {
                if (localStorage.getItem("anoConfig") != $(this).val()) {
                    localStorage.setItem("ultimaClasse", 0);
                }
                localStorage.setItem("anoConfig", $(this).val());

                $("#ano").html(localStorage.getItem("anoConfig"));
                sendSelecionarAno(localStorage.getItem("anoConfig"));
                $(".selecionarAno").removeClass("text-warning");
                $(".selecionarAno").removeClass("bg-dark");

                $(this).addClass("text-warning");
                $(this).addClass("bg-dark");


            });
            $("#" + localStorage.getItem("anoConfig")).addClass("text-warning");
            $("#" + localStorage.getItem("anoConfig")).addClass("bg-dark");

        }


    });
}
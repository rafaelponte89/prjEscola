$(document).ready(() => {


  function verificarConfiguracao() {

    //Carregar seleção versão
    if (localStorage.getItem("completa")) {
      //$("#topo").show();
      $("#menu").show();
      $("#versaoCompleta").prop("checked", true);
    } else {
      //$("#topo").hide();
      $("#menu").hide();
      $("#versaoCompleta").prop("checked", false);
    }

    //Carregar filtros
    if (localStorage.getItem("filtro")) {
      //$("#topo").show();
      if (localStorage.getItem("filtro") === "a") {
        $("#ativos").prop("checked", true);
      } else {
        $("#todos").prop("checked", true);
      }
    }




    carregarAno();
    setarConfigOperador();
  }

  function selecionarVersao() {
    $("#salvarConfig").click(() => {
      if ($("#versaoCompleta").prop("checked") == true) {
        localStorage.setItem("completa", true);
      } else {
        localStorage.removeItem("completa");
      }
    });

    $("#configuracoesModal").on("hidden.bs.modal", function (e) {
      if ($("#versaoCompleta").prop("checked") == true) {
        localStorage.setItem("completa", true);
      } else {
        localStorage.removeItem("completa");
      }
    });
  }
  selecionarVersao();

  var salvarConfig = document.getElementById("salvarConfig");
  var anoConfig = document.getElementById("anoConfig");

  //quando clica no botão salvar de configuração
  salvarConfig.addEventListener("click", function () {
    setarConfigAno();
    verificarConfiguracao();
    setarConfigOperador();
  });

  $("#configuracoesModal").on("hidden.bs.modal", function (e) {
    setarConfigAno();
    verificarConfiguracao();
    setarConfigOperador();
  });

  $("#todos").change(() => {
    alert("todos");
    localStorage.setItem("filtro", "t");
  });
  $("#ativos").change(() => {
    localStorage.setItem("filtro", "a");
  });

  function setarConfigOperador() {
    if (localStorage.getItem("nomeOperador")) {
      if (
        $("#nomeOperador").val() !== "" &&
        $("#cargoOperador").val() !== "" &&
        $("#rgOperador").val() !== ""
      ) {
        document.getElementById("nomeOperador").value = localStorage.setItem(
          "nomeOperador",
          $("#nomeOperador").val()
        );
        document.getElementById("cargoOperador").value = localStorage.setItem(
          "cargoOperador",
          $("#cargoOperador").val()
        );
        document.getElementById("rgOperador").value = localStorage.setItem(
          "rgOperador",
          $("#rgOperador").val()
        );
      }
    } else {
      localStorage.setItem("nomeOperador", $("#nomeOperador").val());
      localStorage.setItem("cargoOperador", $("#cargoOperador").val());
      localStorage.setItem("rgOperador", $("#rgOperador").val());
    }
    document.getElementById("nomeOperador").value =
      localStorage.getItem("nomeOperador");
    document.getElementById("cargoOperador").value =
      localStorage.getItem("cargoOperador");
    document.getElementById("rgOperador").value =
      localStorage.getItem("rgOperador");
  }

  function setarConfigAno() {
    if (localStorage.getItem("anoConfig")) {
      if ($("#anoConfig").val() !== "") {
        localStorage.setItem("anoConfig", $("#anoConfig").val());
      }
    }
  }

  function carregarAno() {
    //Carregar ano Configuração
    if (localStorage.getItem("anoConfig")) {
      document.getElementById("ano").innerHTML =
        localStorage.getItem("anoConfig");
      document.getElementById("anoConfig").value =
        localStorage.getItem("anoConfig");
    } else {
      const date = new Date();
      const currentYear = date.getFullYear();
      localStorage.setItem("anoConfig", currentYear);
      document.getElementById("ano").innerHTML =
        localStorage.getItem("anoConfig");
      document.getElementById("anoConfig").value =
        localStorage.getItem("anoConfig");
    }
  }

  verificarConfiguracao();



});

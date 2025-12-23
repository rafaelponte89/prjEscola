$(document).ready(() => {
    function verificarConfiguracao() {
      const completa = localStorage.getItem("completa") === "true"; // Converte para booleano
      $("#menu").toggle(completa); // Usa diretamente o booleano
      $("#versaoCompleta").prop("checked", completa);
  
      const filtro = localStorage.getItem("filtro");
      $("#ativos").prop("checked", filtro === "a");
      $("#todos").prop("checked", filtro !== "a");
  
      carregarAno();
      setarConfigOperador();
    }
  
    function selecionarVersao() {
      const salvarConfiguracoes = () => {
        localStorage.setItem("completa", $("#versaoCompleta").prop("checked") ? "true" : "false"); // Armazena como string "true" ou "false"
        setarConfigAno();
        verificarConfiguracao();
      };
  
      $("#salvarConfig").click(salvarConfiguracoes);
      $("#configuracoesModal").on("hidden.bs.modal", salvarConfiguracoes);
    }
  
    function setarConfigOperador() {
      ["nomeOperador", "cargoOperador", "rgOperador"].forEach(item => {
        const valor = $("#" + item).val();
        if (valor) localStorage.setItem(item, valor);
        $("#" + item).val(localStorage.getItem(item));
      });
    }
  
    function setarConfigAno() {
      const ano = $("#anoConfig").val();
      // Se ano diferente zera ultima classe
      if (ano != localStorage.getItem("anoConfig")){
        localStorage.setItem("ultimaClasse", 0);
      }
      if (ano) localStorage.setItem("anoConfig", ano);
    }
  
    function carregarAno() {
      const anoConfig = localStorage.getItem("anoConfig") || new Date().getFullYear();
      $("#ano").text(anoConfig);
      $("#anoConfig").val(anoConfig);
      localStorage.setItem("anoConfig", anoConfig);
    }
  
    $("#todos, #ativos").change(function () {
      localStorage.setItem("filtro", this.id === "ativos" ? "a" : "t");
    });
  
    verificarConfiguracao();
    selecionarVersao(); // Chamada da função que estava faltando
  });
  
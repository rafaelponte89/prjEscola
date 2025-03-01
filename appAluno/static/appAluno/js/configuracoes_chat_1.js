// 12/09/2024 otimizado com GPT
$(document).ready(() => {
  function verificarConfiguracao() {
    const completa = localStorage.getItem("completa");
    alert(completa);
    $("#menu").toggle(!!completa);
    $("#versaoCompleta").prop("checked", !!completa);

    const filtro = localStorage.getItem("filtro");
    $("#ativos").prop("checked", filtro === "a");
    $("#todos").prop("checked", filtro !== "a");

    carregarAno();
    setarConfigOperador();

  }

  function selecionarVersao() {
    const salvarConfiguracoes = () => {
      localStorage.setItem("completa", $("#versaoCompleta").prop("checked") ? true : null);
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
      localStorage.setItem("ultimaClasse",0);
      
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
});



window.Relatorios = {
  urls: {},
  init(urls) {
    this.urls = urls;

    $(document).ready(() => {

    });
  },

  renderizarPdf(response) {
    var blob = new Blob([response], { type: "application/pdf" });

    if (window.navigator && window.navigator.msSaveOrOpenBlob) {
      window.navigator.msSaveOrOpenBlob(blob); // for IE
    } else {
      var fileURL = URL.createObjectURL(blob);
      var newWin = window.open(fileURL);
      newWin.focus();
    }
  },

  sendBaixarPdf(rmi, rmf) {
    const url = this.urls.relatorio_rm;
    $.post({
      url: url,
      data: {
        rmi: rmi,
        rmf: rmf,
      },
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      success: (response) => {
        Relatorios.renderizarPdf(response);
      },
    });
  },

  sendBaixarListaPersonalizavel(classe) {
    const url = this.urls.relatorio_personalizavel;
    $.post({
      url: url,
      // datatype: 'pdf',
      data: {
        classe: classe,
        titulo: $("#titulo").val(),
        colunas: $("#colunas").val(),
        tam_colunas: $("#tamanho").val(),
        pagina: $("#pagina").val(),
        repeticao: $("#repeticao").val(),
        tamanho_fonte: $("#tamanho_fonte").val(),
      },
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      success: (response) => {
        Relatorios.renderizarPdf(response);

      },
    });
  },

  sendBaixarDeclaracao(rm) {
    const url = this.urls.declaracao_matricula;
    $.post({
      url: url,
      // datatype: 'pdf',
      data: {
        rm: rm,
        nome_op: localStorage.getItem("nomeOperador"),
        cargo_op: localStorage.getItem("cargoOperador"),
        rg_op: localStorage.getItem("rgOperador"),
      },
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      success: (response) => {
        Relatorios.renderizarPdf(response);

      },
    });
  },

  sendBaixarListaTelefonica(classe) {
    const url = this.urls.lista_telefonica;
    $.post({
      url: url,
      // datatype: 'pdf',
      data: {
        classe: classe,
      },
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
      success: (response) => {
        Relatorios.renderizarPdf(response);

      },
    });
  }

}
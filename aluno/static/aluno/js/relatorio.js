

function renderizarPdf(response) {
  var blob = new Blob([response], { type: "application/pdf" });

  if (window.navigator && window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(blob); // for IE
  } else {
    var fileURL = URL.createObjectURL(blob);
    var newWin = window.open(fileURL);
    newWin.focus();
  }
}

function sendBaixarPdf(rmi, rmf) {
  const url = $("#urls").data("relatorio-rm")
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
      renderizarPdf(response);
    },
  });
}

function sendBaixarListaPersonalizavel(classe) {
  const url = $("#urls").data("relatorio-personalizavel")
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
      renderizarPdf(response);

    },
  });
}

function sendBaixarDeclaracao(rm) {
  const url = $("#urls").data("declaracao-matricula")
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
      renderizarPdf(response);

    },
  });
}

function sendBaixarListaTelefonica(classe) {
  const url = $("#urls").data("lista-telefonica")
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
      renderizarPdf(response);

    },
  });
}
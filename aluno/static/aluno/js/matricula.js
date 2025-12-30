

  function exibirHistoricoMatriculas(rm) {
    $.post({
      url: "{% url 'buscarHistoricoMatriculas' %}",

      headers: {
        "X-CSRFToken": csrftoken,
      },
      data: {
        rm: rm,
      },
      success: (response) => {
        $("#dados").html(response);
      },
      fail: (response) => { },
    });
  }



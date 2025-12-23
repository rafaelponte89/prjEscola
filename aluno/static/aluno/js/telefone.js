function addTelefone() {
    $.get({
        url: "{% url 'contato' %}",
        success: (response) => {
            $("#dados").append(response)

        },
        fail: () => { },
    });
}

function sendDelTelefone(idTel) {
    $.post({
        url: "{% url 'delTelefone' %}",
        headers: {
            "X-CSRFToken": csrftoken,
        },
        data: {
            id_tel: idTel,
        },
        success: (response) => {
            console.log("response");
        },
    });
}

function telefonesAlunos(rm) {
    $.post({
        url: "{% url 'buscarTelefonesAluno' %}",

        headers: {
            "X-CSRFToken": csrftoken,
        },
        data: {
            rm: rm,
        },
        success: (response) => {
            $("#dados").html(response);
            $("#addTelefone").click(() => {
                addTelefone();
                delTelefone();
            });
            delTelefone();
        },
        fail: (response) => { },
    });
}

function delTelefone() {
    var close = document.getElementsByClassName("removerTelefone");
    var i;
    for (i = 0; i < close.length; i++) {
        close[i].onclick = function () {
            var div = this.parentElement;
            sendDelTelefone(this.value);
            div.remove();
        };
    }
}
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

$.ajaxSetup({
    headers: {
        "X-CSRFToken": getCSRFToken()
    }
});
window.Telefones = {
    urls: {},

    init() {

        $(document).ready(() => {
            this.bindEvents();
        });
    },
    bindEvents() {

        $(document).on('click', '.removerTelefone', function () {
            const row = $(this).closest('.telefone');      // Linha do formset
            const checkbox = row.find('input[type="checkbox"]'); // Checkbox hidden do DELETE

            if (checkbox.prop('checked')) {
                // Se já estava marcado: desmarca DELETE
                checkbox.prop('checked', false);
                row.removeClass('telefone-removido');
                $(this)
                    .removeClass('btn-secondary')
                    .addClass('btn-danger');
            } else {
                // Marca DELETE
                checkbox.prop('checked', true);
                row.addClass('telefone-removido');
                $(this)
                    .removeClass('btn-danger')
                    .addClass('btn-secondary');
            }
        });

        $(document).on("click",'#addTelefone', function() {
            const container = $('#listaTelefone');  // onde os forms serão inseridos
            const totalForms = $('#id_telefones-TOTAL_FORMS'); // do management_form
            let formIdx = parseInt(totalForms.val());

            // Clona o empty_form
            const newRow = $('#empty-form .telefone').clone(true, true);

            // Substitui __prefix__ pelo índice correto
            newRow.html(newRow.html().replace(/__prefix__/g, formIdx));

            container.append(newRow);

            totalForms.val(formIdx + 1);
        });




    }

}
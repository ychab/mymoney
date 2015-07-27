;(function($){

    $(document).ready(function() {

        $('.bt-tooltip').tooltip();

        // Fieldset icon collapse/uncollapse
        $(".collapse")
        .on('show.bs.collapse', function() {

          $('.collapse-indicator', $(this).siblings('.panel-heading'))
            .removeClass('glyphicon-collapse-down')
            .addClass('glyphicon-collapse-up');
        })
        .on('hide.bs.collapse', function() {

          $('.collapse-indicator', $(this).siblings('.panel-heading'))
            .removeClass('glyphicon-collapse-up')
            .addClass('glyphicon-collapse-down');
        });

        // Modal open by click with AJAX content load.
        $('.modal-summary-link').click(function(e) {
            var $modal = $('#modal-summary')
            var href = $(this).attr('href');
            e.preventDefault();

            $.ajax({
                url: href,
                success: function(data, textStatus) {
                    $('.modal-body', $modal).html(data)
                    $modal.modal('show')
                }
            })
        });

        // Checkbox (de)select all.
        $('table.check-all').each(function(e) {
            $container = $(this)
            $checkbox = $('<input type="checkbox" id="checkbox-all">').appendTo(
                $('thead > tr > th:first', $container)
            )

            $checkbox.click(function(e) {
                $(':checkbox:not(#checkbox-all)', $container).prop(
                    'checked',
                    $(this).prop('checked')
                );
            });
        });

    });

})(jQuery);

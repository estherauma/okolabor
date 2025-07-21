$(document).ready(function () {
        // When #select-all-workers is clicked
        $('#select-all-shortlist').on('change', function () {
            let isChecked = $(this).is(':checked');
            $('.worker-checkbox').prop('checked', isChecked);
        });

        // If any single checkbox is unchecked, uncheck the "select all"
        $('.worker-checkbox').on('change', function () {
            if (!$(this).is(':checked')) {
                $('#select-all-shortlist').prop('checked', false);
            } else {
                // Check if all checkboxes are checked, then check "select all"
                if ($('.worker-checkbox:checked').length === $('.worker-checkbox').length) {
                    $('#select-all-shortlist').prop('checked', true);
                }
            }
        });
    });
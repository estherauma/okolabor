$(document).ready(function () {
    // Fix for select2 inside bootstrap modal
    $.fn.modal.Constructor.prototype._enforceFocus = function() {};

    const workRequestSelect = $('#modal_work_request');
    workRequestSelect.select2({
        placeholder: "Search for job orders...",
        width: '100%',
        allowClear: true,
        minimumResultsForSearch: 0
    });

    workRequestSelect.on('change', function() {
        const workRequestId = $(this).val();
        const roleSelect = document.getElementById('modal_role');

        if (workRequestId) {
            fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    data.roles.forEach(role => {
                        const option = document.createElement('option');
                        option.value = role.id;
                        option.textContent = role.title;
                        roleSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching roles:', error);
                });
        }
    });
});

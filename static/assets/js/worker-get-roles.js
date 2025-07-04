$(document).ready(function () {
    const workRequestSelect = $('#modal_work_request');
    const roleSelect = $('#modal_role');

    workRequestSelect.select2({
        placeholder: "Search for job orders...",
        width: '59%',
        allowClear: true,
        minimumResultsForSearch: 0
    });

    workRequestSelect.on('change', function () {
        const workRequestId = $(this).val();

        roleSelect.html('<option value="">{% translate "workersListSelectARole" %}</option>');

        if (workRequestId) {
            fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Roles fetched:', data.roles);
                    data.roles.forEach(role => {
                        const option = $('<option></option>')
                            .val(role.id)
                            .text(role.title);
                        roleSelect.append(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching roles:', error);
                });
        }
    });
});
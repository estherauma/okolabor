
document.addEventListener('DOMContentLoaded', function() {
    const workRequestSelect = document.getElementById('modal_work_request_{{ worker.id }}');
    const roleSelect = document.getElementById('modal_role_{{ worker.id }}');

    workRequestSelect.addEventListener('change', function() {
        const workRequestId = this.value;
        if (workRequestId) {
            fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
                .then(response => response.json())
                .then(data => {
                    // Clear existing options
                    roleSelect.innerHTML = '<option value="">{% translate "workersListSelectARole" %}</option>';

                    // Add new options
                    data.roles.forEach(role => {
                        const option = document.createElement('option');
                        option.value = role.id;
                        option.textContent = role.title;
                        roleSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching roles:', error));
        } else {
            // Clear the roles dropdown if no work request is selected
            roleSelect.innerHTML = '<option value="">{% translate "workersListSelectARole" %}</option>';
        }
    });
});
$(document).ready(function () {
    // Fix for select2 inside bootstrap modal
    $.fn.modal.Constructor.prototype._enforceFocus = function() {};

    const workRequestSelect = $('#modal_work_request');
    workRequestSelect.select2({
        
        width: '100%',
        allowClear: true,
        minimumResultsForSearch: 0
    });
})

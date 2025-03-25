document.getElementById('modal_work_request').addEventListener('change', function() {
    const workRequestId = this.value;
    const roleSelect = document.getElementById('modal_role');

    // Clear previous options
    roleSelect.innerHTML = '<option value="">{% translate "selectARole" %}</option>';

    if (workRequestId) {
        fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
            .then(response => response.json())
            .then(data => {
                data.roles.forEach(role => {
                    const option = document.createElement('option');
                    option.value = role.id;
                    option.textContent = role.title;
                    roleSelect.appendChild(option);
                });
            });
    }
});


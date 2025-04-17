document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.worker-checkbox');
    const addToShortlistBtn = document.getElementById('addToShortlistBtn');

    // Enable/disable the "Add to Shortlist" button based on checkbox selection
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
            addToShortlistBtn.disabled = !anyChecked;
        });
    });

    addToShortlistBtn.addEventListener('click', function() {
        const selectedWorkerIds = Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        // Retrieve work_request_id and role_id from hidden inputs
        const workRequestId = document.getElementById('workRequestId').value;
        const roleId = document.getElementById('roleId').value;

        // Send the selected worker IDs, work_request_id, and role_id to the server
        fetch('/add-to-shortlist/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                workerIds: selectedWorkerIds,
                workRequestId: workRequestId,
                roleId: roleId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding workers to the shortlist.');
        });
    });
});

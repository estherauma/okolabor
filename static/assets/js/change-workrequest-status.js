document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('saveStatusBtn').addEventListener('click', function () {
        const selectedStatus = document.getElementById('statusFilter').value;
        const selectedWorkRequests = [];
        document.querySelectorAll('.row-checkbox:checked').forEach(checkbox => {
            selectedWorkRequests.push(checkbox.getAttribute('data-id'));
        });
        if (selectedWorkRequests.length > 0) {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch('/update-status/', {
                method: 'POST',
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    work_requests: selectedWorkRequests,
                    status: selectedStatus
                })
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            }).then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    console.log(data.error);
                }
            }).catch(err => {
                alert('An error occurred: ' + err.message);
            });
        } else {
            alert('Please select at least one work request');
        }
    });
});
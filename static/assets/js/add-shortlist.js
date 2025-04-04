document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.worker-checkbox');
    const addToShortlistBtn = document.getElementById('addToShortlistBtn');

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

        // Send the selected worker IDs to the server
        fetch('/add-to-shortlist/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ workerIds: selectedWorkerIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Workers added to shortlist!');
                // Optionally, update the UI to reflect the changes
            } else {
                alert('Failed to add workers to shortlist.');
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.allworkers-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllAllWorkers');
    const addToShortlistBtn = document.getElementById('addToShortlistBtn');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            toggleAddButton();
        });
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            toggleAddButton();

            // Sync "Select All" checkbox status
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            selectAllCheckbox.checked = allChecked;
        });
    });

    function toggleAddButton() {
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        addToShortlistBtn.disabled = !anyChecked;
    }

    // ✅ Add to Shortlist click handler
    addToShortlistBtn.addEventListener('click', function () {
        const selectedWorkerIds = Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const workRequestId = document.getElementById('workRequestId').value;
        const roleId = document.getElementById('roleId').value;

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
            location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding workers to the shortlist.');
        });
    });
});

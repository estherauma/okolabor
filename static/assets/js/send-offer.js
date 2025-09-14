document.addEventListener('DOMContentLoaded', function () {
    // === Select All Functionality ===
    const setupSelectAll = (selectAllId, checkboxClass) => {
        const selectAll = document.getElementById(selectAllId);
        const checkboxes = document.querySelectorAll(checkboxClass);

        if (selectAll) {
            // When "Select All" is toggled
            selectAll.addEventListener('change', function () {
                checkboxes.forEach(cb => cb.checked = this.checked);
            });

            // Sync "Select All" status if individual checkboxes are changed
            checkboxes.forEach(cb => {
                cb.addEventListener('change', function () {
                    const allChecked = Array.from(checkboxes).every(c => c.checked);
                    selectAll.checked = allChecked;
                });
            });
        }
    };

    // Setup for All Workers and Shortlist tabs
    setupSelectAll('selectAllAllWorkers', '.allworkers-checkbox');
    setupSelectAll('selectAllShortlist', '.worker-shortlist-checkbox');
    const sendOfferBtn = document.getElementById('sendOfferBtn');
    const allworkersSendOfferBtn = document.getElementById('workerSendOfferBtn');

    // Extract pk and role_id from URL
    const urlParts = window.location.pathname.split('/');
    const jobOrderIndex = urlParts.indexOf('job-order');
    const pk = urlParts[jobOrderIndex + 1];
    const role_id = urlParts[jobOrderIndex + 3];

    const updateWorkerStatusUrl = `/job-order/${pk}/add-workers/${role_id}/update-worker-status/`;

    const handleOfferSend = (checkboxClass) => {
        const workerCheckboxes = document.querySelectorAll(`${checkboxClass}:checked`);
        const workerIds = Array.from(workerCheckboxes).map(checkbox => checkbox.value);

        if (workerIds.length === 0) {
            alert("{% translate 'Please select at least one worker.' %}");
            return;
        }

        const formData = new URLSearchParams();
        workerIds.forEach(id => formData.append('worker_ids[]', id));
        formData.append('work_request', pk);
        formData.append('role', role_id); 

        fetch(updateWorkerStatusUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: formData.toString()
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                alert("{% translate 'Failed to update status. Please try again.' %}");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("{% translate 'An error occurred. Please try again.' %}");
        });
    };

    if (sendOfferBtn) {
        sendOfferBtn.addEventListener('click', function () {
            handleOfferSend('.worker-shortlist-checkbox');
        });
    }

    if (allworkersSendOfferBtn) {
        allworkersSendOfferBtn.addEventListener('click', function () {
            handleOfferSend('.allworkers-checkbox');
        });
    }
});

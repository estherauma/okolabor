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

    // Resolve Job Order and Role from dropdowns on this page, or fall back to URL if present
    const getWorkRequestAndRole = () => {
        const workRequestEl = document.getElementById('modal_work_request');
        const roleEl = document.getElementById('modal_role');
        let pk = workRequestEl && workRequestEl.value ? workRequestEl.value : null;
        let role_id = roleEl && roleEl.value ? roleEl.value : null;

        // Fallback to URL structure /job-order/<pk>/add-workers/<role_id>/...
        if (!pk || !role_id) {
            const parts = window.location.pathname.split('/').filter(Boolean);
            const jobOrderIdx = parts.indexOf('job-order');
            if (jobOrderIdx !== -1) {
                pk = pk || parts[jobOrderIdx + 1];
                role_id = role_id || parts[jobOrderIdx + 3];
            }
        }
        return { pk, role_id };
    };

    const handleOfferSend = (checkboxClass) => {
        const { pk, role_id } = getWorkRequestAndRole();

        if (!pk || !role_id) {
            alert('Please select a Job Order and Role first.');
            return;
        }

        const workerCheckboxes = document.querySelectorAll(`${checkboxClass}:checked`);
        const workerIds = Array.from(workerCheckboxes).map(checkbox => checkbox.value);

        if (workerIds.length === 0) {
            alert("{% translate 'Please select at least one worker.' %}");
            return;
        }

        const updateWorkerStatusUrl = `/job-order/${pk}/add-workers/${role_id}/update-worker-status/`;

        const formData = new URLSearchParams();
        workerIds.forEach(id => formData.append('worker_ids[]', id));
        formData.append('work_request', pk);
        formData.append('role', role_id);

        fetch(updateWorkerStatusUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
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

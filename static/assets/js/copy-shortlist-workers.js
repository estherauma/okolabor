document.addEventListener('DOMContentLoaded', function () {
    const copyBtn = document.getElementById('copyBtn');
    const workerCheckboxes = document.querySelectorAll('.worker-shortlist-checkbox');
    const copyForm = document.getElementById('copyForm');
    const targetWorkRequestSelect = document.getElementById('target_work_request');
    const roleSelect = document.getElementById('role_id');

    const copyUrl = copyForm.dataset.url;
    const getRolesUrl = copyForm.dataset.getRolesUrl;
    const csrfToken = copyForm.dataset.csrf;
    copyBtn.addEventListener('click', function () {
        workerCheckboxes.forEach(checkbox => {
            checkbox.checked = true;
        });

        const modalEl = document.getElementById('copyModal');
        if (modalEl) {
            const copyModal = new bootstrap.Modal(modalEl);
            copyModal.show();
        } else {
            console.error('❌ copyModal element not found!');
        }
    });

    targetWorkRequestSelect.addEventListener('change', function () {
        const workRequestId = this.value;
        if (workRequestId) {
            fetch(`${getRolesUrl}?work_request_id=${workRequestId}`)
                .then(response => response.json())
                .then(data => {
                    roleSelect.innerHTML = '<option value="" disabled selected>Select a role</option>';
                    data.roles.forEach(role => {
                        const option = document.createElement('option');
                        option.value = role.id;
                        option.textContent = role.title;
                        roleSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error loading roles:', error);
                });
        } else {
            roleSelect.innerHTML = '<option value="" disabled selected>Select a role</option>';
        }
    });

    copyForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const selectedWorkers = Array.from(workerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        if (selectedWorkers.length === 0) {
            alert('Please select at least one worker.');
            return;
        }

        const formData = new FormData(copyForm);
        selectedWorkers.forEach(workerId => {
            formData.append('worker_ids[]', workerId);
        });

        fetch(copyUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Failed to copy workers.');
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            alert('An error occurred while copying workers.');
        });
    });
});

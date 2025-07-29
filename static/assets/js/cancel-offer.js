document.addEventListener('DOMContentLoaded', function () {
    const btnShortlist = document.getElementById('cancel-offer-shortlist');
    const btnOffersent = document.getElementById('cancel-offer-offersent');
    const btnConfirmlist = document.getElementById('cancel-confirmed-btn');

    // === Select All Setup Function ===
    const setupSelectAll = (selectAllId, checkboxClass, checkboxNameAttr) => {
        const selectAll = document.getElementById(selectAllId);
        const checkboxes = document.querySelectorAll(`input[name="${checkboxNameAttr}"]`);

        if (selectAll) {
            // Select/Deselect all checkboxes when selectAll is toggled
            selectAll.addEventListener('change', function () {
                checkboxes.forEach(cb => cb.checked = this.checked);
            });

            // Sync selectAll checkbox state based on individual checkbox changes
            checkboxes.forEach(cb => {
                cb.addEventListener('change', function () {
                    const allChecked = Array.from(checkboxes).every(c => c.checked);
                    selectAll.checked = allChecked;
                });
            });
        }
    };

    // === Call Select All Setup for Each Tab ===
    setupSelectAll('selectAllShortlist', '.worker-shortlist-checkbox', 'worker-shortlist-checkbox');
    setupSelectAll('selectAlloffersent', '.worker-offersent-checkbox', 'worker-offersent-checkbox');
    setupSelectAll('selectAllConfirmed', '.worker-confirmed-checkbox', 'worker-confirmed-checkbox');

    // === Handle Cancel Buttons ===
    if (btnShortlist) {
        btnShortlist.addEventListener('click', function () {
            handleCancel('worker-shortlist-checkbox');
        });
    }

    if (btnOffersent) {
        btnOffersent.addEventListener('click', function () {
            handleCancel('worker-offersent-checkbox');
        });
    }

    if (btnConfirmlist) {
        btnConfirmlist.addEventListener('click', function () {
            handleCancel('worker-confirmed-checkbox');
        });
    }

    function handleCancel(checkboxName) {
        const checkboxes = document.querySelectorAll(`input[name="${checkboxName}"]:checked`);
        const workerIds = Array.from(checkboxes).map(cb => cb.value);

        if (workerIds.length > 0) {
            fetch('/cancel-offer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ worker_ids: workerIds })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    alert('Failed to cancel offer.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        } else {
            alert('Please select at least one worker.');
        }
    }
});

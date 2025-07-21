document.addEventListener('DOMContentLoaded', function () {
    const btnShortlist = document.getElementById('cancel-offer-shortlist');
    const btnOffersent = document.getElementById('cancel-offer-offersent');
    const btnConfirmlist = document.getElementById('cancel-confirmed-btn');


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

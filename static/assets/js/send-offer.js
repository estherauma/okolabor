const updateWorkerStatusUrl = '/update-worker-status/';

document.addEventListener('DOMContentLoaded', function () {
    const sendOfferBtn = document.getElementById('sendOfferBtn');
    if (sendOfferBtn) {
        sendOfferBtn.addEventListener('click', function() {
            console.log("sendOfferBtn clicked");
            const workerCheckboxes = document.querySelectorAll('.worker-shortlist-checkbox:checked');
            const workerIds = Array.from(workerCheckboxes).map(checkbox => checkbox.value);

            console.log(workerCheckboxes, "workerCheckboxes");
            console.log(workerIds,"workerIds");

            if (workerIds.length === 0) {
                alert("{% translate 'Please select at least one worker.' %}");
                return;
            }

            fetch(updateWorkerStatusUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: 'worker_ids[]=' + workerIds.join('&worker_ids[]=')
            })
            .then(response => response.json())
            .then(data => {
                console.log(data, "data");
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
        });
    } else {
        console.error("Element with ID 'sendOfferBtn' not found in the DOM.");
    }
    });

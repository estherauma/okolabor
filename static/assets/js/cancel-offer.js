document.addEventListener('DOMContentLoaded', function () {
    const cancelOfferBtn = document.getElementById('cancel-offer-btn');
    console.log("cancelOfferBtn", cancelOfferBtn);
    
    if (cancelOfferBtn) {
        console.log("cancelOfferBtn found in the DOM");
        cancelOfferBtn.addEventListener('click', function () {
            console.log("Cancel offer button clicked");
            let workerIds = [];

            let checkboxes = document.querySelectorAll('input[name="worker-offer-checkbox"]:checked');
            console.log("Checkboxes selected:", checkboxes.length);

            if (checkboxes.length === 0) {
                checkboxes = document.querySelectorAll('input[name="worker-shortlist-checkbox"]:checked');
            }

            console.log("Checkboxes found:", checkboxes.length);
            console.log("Checkboxes selected:", checkboxes);

            checkboxes.forEach(function (checkbox) {
                workerIds.push(checkbox.value);
            });

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
        });
    } else {
        console.error("Element with ID 'cancel-offer-btn' not found.");
    }
});

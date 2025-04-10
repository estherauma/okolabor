document.getElementById('cancel-offer-btn').addEventListener('click', function() {
    var workerIds = [];
    var checkboxes = document.querySelectorAll('input[name="worker_ids"]:checked');
    checkboxes.forEach(function(checkbox) {
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
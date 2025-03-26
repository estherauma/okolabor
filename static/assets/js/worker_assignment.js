document.addEventListener("DOMContentLoaded", function() {
    const assignButton = document.querySelector(".dark-green-button"); // Button to open modal
    const workerCheckboxes = document.querySelectorAll(".worker-checkbox");
    const modalWorkerName = document.getElementById("modal_worker_name");
    const modalWorkerId = document.getElementById("modal_worker_id");

    function updateAssignButtonState() {
        const isAnyChecked = Array.from(workerCheckboxes).some(checkbox => checkbox.checked);
        assignButton.disabled = !isAnyChecked; // Enable if at least one checkbox is checked
    }

    // Add event listeners to checkboxes to update the button state
    workerCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateAssignButtonState);
    });

    assignButton.addEventListener("click", function() {
        let selectedWorkers = [];
        let selectedWorkerIds = [];

        workerCheckboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                selectedWorkers.push(checkbox.getAttribute("data-worker-name"));
                selectedWorkerIds.push(checkbox.value);
            }
        });

        // Show selected worker names in the modal input
        modalWorkerName.value = selectedWorkers.join(", ");
        // Store selected worker IDs in the hidden input
        modalWorkerId.value = selectedWorkerIds.join(",");
    });

    // Initial state check (in case checkboxes are pre-checked)
    updateAssignButtonState();
});

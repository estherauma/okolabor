document.addEventListener("DOMContentLoaded", function() {
    const assignButton = document.querySelector(".dark-green-button");
    const workerCheckboxes = document.querySelectorAll(".worker-checkbox");
    const modalWorkerName = document.getElementById("modal_worker_name");
    const modalWorkerId = document.getElementById("modal_worker_id");

    function updateAssignButtonState() {
        const isAnyChecked = Array.from(workerCheckboxes).some(checkbox => checkbox.checked);
        assignButton.disabled = !isAnyChecked; 
    }

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

        modalWorkerName.value = selectedWorkers.join(", ");
        
        modalWorkerId.value = selectedWorkerIds.join(",");
    });

   
    updateAssignButtonState();
});
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    const shortlistBtn = document.getElementById("addToShortlistBtn");
    const sendOfferBtn = document.getElementById("sendOfferBtnDirectly");
    // Use a live NodeList or querySelectorAll and convert to Array when needed
    const workerCheckboxes = document.querySelectorAll(".worker-checkbox"); 
    const workRequestSelect = document.getElementById("modal_work_request");
    const roleSelect = document.getElementById("modal_role");

    function toggleButtonState() {
        const anyWorkerChecked = Array.from(workerCheckboxes).some(cb => cb.checked);
        const jobOrderAndRoleSelected = workRequestSelect.value && roleSelect.value;

        // Logic for Shortlist button: Only requires workers to be checked
        shortlistBtn.disabled = !anyWorkerChecked;

        // Logic for Send Offer button: Requires workers to be checked AND job order/role selected
        sendOfferBtn.disabled = !(anyWorkerChecked && jobOrderAndRoleSelected);
    }

    // Add event listeners to all relevant elements that affect button state
    workerCheckboxes.forEach(cb => {
        cb.addEventListener("change", toggleButtonState);
    });

    workRequestSelect.addEventListener("change", toggleButtonState);
    roleSelect.addEventListener("change", toggleButtonState);

    // Set initial button states on page load
    toggleButtonState();

    // Shortlist Button Click Handler
    shortlistBtn.addEventListener("click", function () {
        const selectedWorkers = Array.from(workerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const workRequest = workRequestSelect.value;
        const role = roleSelect.value;

        // Re-validate just before sending, in case state changed rapidly
        if (selectedWorkers.length === 0) {
            alert("Please select at least one worker to shortlist.");
            return; // Stop execution if validation fails
        }
        if (!workRequest || !role) {
            alert("Please select both a Work Request and a Role to shortlist.");
            return;
        }


        const csrftoken = getCookie("csrftoken");

        fetch("/assign-worker/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                worker_ids: selectedWorkers.join(","),
                work_request: workRequest,
                role: role,
                status: "assigned"
            })
        })
        .then(response => {
            if (!response.ok) {
                // Handle HTTP errors (e.g., 400, 500)
                return response.json().then(errorData => {
                    throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Consider showing a success message instead of immediate reload
                // alert(data.message); 
                window.location.reload();
            } else {
                alert(data.message || "Shortlisting failed.");
            }
        })
        .catch(err => {
            console.error("Error shortlisting:", err);
            alert("Something went wrong during shortlisting: " + err.message); // Display error message
        });
    });

    // Send Offer Button Click Handler
    sendOfferBtn.addEventListener("click", function () {
        const selectedWorkers = Array.from(workerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const workRequest = workRequestSelect.value;
        const role = roleSelect.value;

        // Re-validate rigorously for sending offers
        if (!workRequest || !role) {
            alert("Please select both a Work Request and a Role to send an offer.");
            return; // Stop execution if validation fails
        }

        console.log("Selected Workers:", selectedWorkers.length);

        if (selectedWorkers.length === 0) {
           
            alert("Please select at least one worker to send an offer.");
            return; // Stop execution if validation fails
        }

        const csrftoken = getCookie("csrftoken");

        fetch("/send-offer/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                worker_ids: selectedWorkers.join(","),
                work_request: workRequest,
                role: role,
                status: "offersent"
            })
        })
        .then(response => {
            if (!response.ok) {
                // Handle HTTP errors (e.g., 400, 500)
                return response.json().then(errorData => {
                    throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // alert(data.message); 
                window.location.reload();
            } else {
                alert(data.message || "Sending offer failed.");
            }
        })
        .catch(err => {
            console.error("Error sending offer:", err);
            alert("Something went wrong while sending the offer: " + err.message); // Display error message
        });
    });
});
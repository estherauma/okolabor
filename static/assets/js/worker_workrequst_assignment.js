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
    let workerCheckboxes = document.querySelectorAll(".worker-checkbox");
    const workRequestSelect = document.getElementById("modal_work_request");
    const roleSelect = document.getElementById("modal_role");
    const selectAllCheckbox = document.getElementById("select-all-workers");  

    // Toggle Button State
    function toggleButtonState() {
        const anyWorkerChecked = Array.from(workerCheckboxes).some(cb => cb.checked);
        const jobOrderAndRoleSelected = workRequestSelect.value && roleSelect.value;

        shortlistBtn.disabled = !anyWorkerChecked;
        sendOfferBtn.disabled = !(anyWorkerChecked && jobOrderAndRoleSelected);
    }

    // Handle Select All checkbox
    selectAllCheckbox.addEventListener("change", function () {
        const isChecked = this.checked;
        workerCheckboxes.forEach(cb => cb.checked = isChecked);
        toggleButtonState();
    });

    // Handle individual checkbox changes
    // workerCheckboxes.forEach(cb => {
    //     cb.addEventListener("change", function () {
    //         if (!this.checked) {
    //             selectAllCheckbox.checked = false;
    //         } else {
    //             const allChecked = Array.from(workerCheckboxes).every(cb => cb.checked);
    //             selectAllCheckbox.checked = allChecked;
    //         }
    //         toggleButtonState();
    //     });
    // });
        document.addEventListener("change", function(e) {
            if (e.target.classList.contains("worker-checkbox")) {
                    workerCheckboxes = document.querySelectorAll(".worker-checkbox");
                if (!e.target.checked) {
                    selectAllCheckbox.checked = false;
                } else {
                    const allChecked = Array.from(workerCheckboxes).every(cb => cb.checked);
                    selectAllCheckbox.checked = allChecked;
                }
                toggleButtonState();
            }
       });

    // Watch dropdown changes too
    workRequestSelect.addEventListener("change", toggleButtonState);
    roleSelect.addEventListener("change", toggleButtonState);

    // Initial state
    toggleButtonState();

    // Shortlist button click
    shortlistBtn.addEventListener("click", function () {
        const selectedWorkers = Array.from(workerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        const workRequest = workRequestSelect.value;
        const role = roleSelect.value;

        if (selectedWorkers.length === 0) {
            alert("Please select at least one worker to shortlist.");
            return;
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
                return response.json().then(errorData => {
                    throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message || "Shortlisting failed.");
            }
        })
        .catch(err => {
            console.error("Error shortlisting:", err);
            alert("Something went wrong during shortlisting: " + err.message);
        });

    });

    // Send Offer button click
    sendOfferBtn.addEventListener("click", function () {
        const selectedWorkers = Array.from(workerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        const workRequest = workRequestSelect.value;
        const role = roleSelect.value;

        if (!workRequest || !role) {
            alert("Please select both a Work Request and a Role to send an offer.");
            return;
        }

        if (selectedWorkers.length === 0) {
            alert("Please select at least one worker to send an offer.");
            return;
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
                return response.json().then(errorData => {
                    throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message || "Sending offer failed.");
            }
        })
        .catch(err => {
            console.error("Error sending offer:", err);
            alert("Something went wrong while sending the offer: " + err.message);
        });
    });
});

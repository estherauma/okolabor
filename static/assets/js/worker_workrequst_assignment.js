
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
    const checkboxes = document.querySelectorAll(".worker-checkbox");

    function toggleButtonState() {
        const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
        shortlistBtn.disabled = !anyChecked;
    }

    checkboxes.forEach(cb => {
        cb.addEventListener("change", toggleButtonState);
    });

    shortlistBtn.addEventListener("click", function () {
        const selectedWorkers = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const workRequest = document.getElementById("modal_work_request").value;
        const role = document.getElementById("modal_role").value;
        console.log("Selected Workers:", selectedWorkers);
        console.log("Work Request:", workRequest);
        console.log("Role:", role);

        if (!workRequest || !role) {
            alert("Please select both a Work Request and a Role.");
            return;
        }

        if (selectedWorkers.length === 0) {
            alert("Please select at least one worker.");
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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert(data.message || "Assignment failed.");
            }
        })
        .catch(err => {
            console.error("Error:", err);
            alert("Something went wrong.");
        });
    });
});
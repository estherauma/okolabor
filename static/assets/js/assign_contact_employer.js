document.getElementById("assignContactBtn").addEventListener("click", function () {
    const employerId = this.getAttribute("data-employer-id");
    document.getElementById("employerIdField").value = employerId;
});

document.getElementById("assignContactForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const employerId = document.getElementById("employerIdField").value;
    const name = document.getElementById("contactName").value;
    const email = document.getElementById("contactEmail").value;
    const phone = document.getElementById("contactPhone").value;
    const position = document.getElementById("contactPosition").value;
    const isPrimary = document.getElementById("isPrimary").checked;

    $("#global-loader").fadeIn("slow");
    document.body.style.overflow = "hidden";

    fetch("/assign-contact/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            employer_id: employerId,
            name: name,
            email: email,
            phone: phone,
            position: position,
            is_primary: isPrimary,
        }),
    })
    .then((response) => {
        if (response.redirected) {
            // In case of redirect from backend, follow it
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then((data) => {
        if (data && data.status === "error") {
            alert("Error: " + data.error);
        } else {
            // ✅ SUCCESS: Close modal and reload page
            $("#assignContactModal").modal("hide");
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    })
    .catch((error) => {
        console.error("Fetch Error:", error);
        alert("An error occurred while assigning contact.");
    })
    .finally(() => {
        $("#global-loader").fadeOut("slow");
        document.body.style.overflow = "auto";
    });
});

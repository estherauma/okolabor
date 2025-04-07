document.getElementById("assignContactForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const selectedEmployers = Array.from(document.querySelectorAll(".table-checkbox:checked"))
        .map((checkbox) => checkbox.closest("tr").getAttribute("data-id"));

    const name = document.getElementById("contactName").value;
    const email = document.getElementById("contactEmail").value;
    const phone = document.getElementById("contactPhone").value;
    const position = document.getElementById("contactPosition").value;
    const isPrimary = document.getElementById("isPrimary").checked;

    if (selectedEmployers.length === 0) {
        alert("Please select at least one employer.");
        return;
    }

    $("#global-loader").fadeIn("slow");
    document.body.style.overflow = "hidden";

    fetch("/assign-contact/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            employer_ids: selectedEmployers,
            name: name,
            email: email,
            phone: phone,
            position: position,
            is_primary: isPrimary,
        }),
    })
    .then((response) => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then((data) => {
        if (data && data.status === "error") {
            alert("Error: " + data.error);
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

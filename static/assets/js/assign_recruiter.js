document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed");

    const assignRecruiterBtn = document.getElementById("assignRecruiterBtn");
    const assignRecruiterModalEl = document.getElementById("assignRecruiterModal");
    const assignRecruiterModal = bootstrap.Modal.getInstance(assignRecruiterModalEl) || 
                                new bootstrap.Modal(assignRecruiterModalEl);

    if (assignRecruiterBtn) {
        assignRecruiterBtn.addEventListener("click", function () {
            let selectedEmployers = [];
            document.querySelectorAll(".table-checkbox:checked").forEach((checkbox) => {
                const employerId = checkbox.closest("tr").dataset.id;
                if (employerId) selectedEmployers.push(employerId);
            });

            let recruiterId = document.getElementById("recruiterSelect").value;

            if (selectedEmployers.length === 0) {
                alert("Please select at least one employer.");
                return;
            }

            if (!recruiterId) {
                alert("Please select a recruiter.");
                return;
            }

            // Show global loader
            $("#global-loader").fadeIn("slow");
            document.body.style.overflow = 'hidden';

            fetch("/send-recruiter-email/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    employer_ids: selectedEmployers,
                    recruiter_id: recruiterId,
                }),
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Email sent successfully!");
                    assignRecruiterModal.hide();
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch((error) => {
                console.error("Fetch Error:", error);
                alert("An error occurred while sending the email.");
            })
            .finally(() => {
                // Hide global loader
                $("#global-loader").fadeOut("slow");
                document.body.style.overflow = 'auto';
            });
        });
    }
});

// Your existing window load handler (keep this separate)
$(window).on("load", function(e) {
    $("#global-loader").fadeOut("slow");
});
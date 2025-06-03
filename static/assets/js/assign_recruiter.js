document.addEventListener("DOMContentLoaded", function () {
    const assignRecruiterBtn = document.getElementById("assignRecruiterBtn");
    const recruiterSelect = document.getElementById("recruiterSelect");

    if (assignRecruiterBtn) {
        assignRecruiterBtn.addEventListener("click", function () {
            let selectedEmployers = [];
            document.querySelectorAll(".table-checkbox:checked").forEach((checkbox) => {
                const employerId = checkbox.closest("tr").dataset.id;
                if (employerId) selectedEmployers.push(employerId);
            });
            const recruiterOrgId = recruiterSelect.value;
            if (selectedEmployers.length === 0) {
                alert("Please select at least one employer.");
                return;
            }

            if (!recruiterOrgId) {
                alert("Please select a recruiter organization.");
                return;
            }

            $("#global-loader").fadeIn("slow");
            document.body.style.overflow = 'hidden';

            fetch("/assign-employers-to-recruiter/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    employer_org_id: selectedEmployers,
                    recruiter_org_id: recruiterOrgId,
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert("Error: " +  (data.message || "Something went wrong."));
                }
            })
            .catch(error => {
                console.error("Fetch Error:", error);
            })
            .finally(() => {
                $("#global-loader").fadeOut("slow");
                document.body.style.overflow = 'auto';
            });
        });
    }
});

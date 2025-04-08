document.addEventListener("DOMContentLoaded", function () {
    const selectedUsersInput = document.getElementById("selectedUsersInput");
    const assignForm = document.getElementById("assignOrganizationForm");
    const assignOrgBtn = document.getElementById("assign-organization-btn");

    // ✅ When user clicks "Assign Organization" button
    assignOrgBtn?.addEventListener("click", function (e) {
        const checkboxes = document.querySelectorAll(".recruiter-checkbox:checked");
        const selectedUserIds = Array.from(checkboxes).map(cb => cb.value.trim()).filter(val => val !== "");

        console.log("Selected checkboxes:", checkboxes.length);
        console.log("Selected User IDs:", selectedUserIds);

        if (selectedUserIds.length === 0) {
            alert("⚠️ Please select at least one user before assigning an organization.");
            // Cancel modal opening
            e.stopPropagation();
            e.preventDefault();
            return false;
        }

        // Set hidden input field value
        selectedUsersInput.value = JSON.stringify(selectedUserIds);
    });

    // ✅ Form submit handler inside modal
    assignForm?.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(assignForm);

        fetch("/account/assign-organization/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("✅ Organization assigned successfully.");
                location.reload();
            } else {
                alert(data.error || "❌ Something went wrong.");
            }
        })
        .catch(err => {
            console.error("Error:", err);
            alert("❌ Failed to assign organization.");
        });
    });

    // ✅ Handle "select all"
    const selectAllCheckbox = document.getElementById("select-all-checkbox");
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            const checkboxes = document.querySelectorAll(".recruiter-checkbox");
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
});

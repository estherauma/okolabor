document.addEventListener("DOMContentLoaded", function () {
    const selectedUsersInput = document.getElementById("selectedUsersInput");
    const assignForm = document.getElementById("assignOrganizationForm");
    const assignOrgBtn = document.getElementById("assign-organization-btn");

    assignOrgBtn?.addEventListener("click", function (e) {
        const checkboxes = document.querySelectorAll(".recruiter-checkbox:checked");
        const selectedUserIds = Array.from(checkboxes).map(cb => cb.value.trim()).filter(val => val !== "");

        if (selectedUserIds.length === 0) {
            alert("⚠️ Please select at least one user before assigning an organization.");
            e.stopPropagation();
            e.preventDefault();
            return false;
        }

        selectedUsersInput.value = JSON.stringify(selectedUserIds);
    });

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

    const selectAllCheckbox = document.getElementById("select-all-checkbox");
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            const checkboxes = document.querySelectorAll(".recruiter-checkbox");
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
});

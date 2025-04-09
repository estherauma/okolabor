document.addEventListener("DOMContentLoaded", function () {
    const selectedUsersInput = document.getElementById("selectedEmployerUsersInput");
    const assignForm = document.getElementById("assignEmployerOrganizationForm");
    const assignOrgBtn = document.getElementById("assign-employer-organization-btn");

    console.log("Selected Users Input:", selectedUsersInput);
    console.log("Assign Form:", assignForm);
    console.log("Assign Org Button:", assignOrgBtn);

    assignOrgBtn?.addEventListener("click", function (e) {
        const checkboxes = document.querySelectorAll(".employer-checkbox:checked");
        console.log("Checked Checkboxes:", checkboxes);

        const selectedUserIds = Array.from(checkboxes).map(cb => cb.value.trim()).filter(val => val !== "");
        console.log("Selected User IDs:", selectedUserIds);

        if (selectedUserIds.length === 0) {
            alert("⚠️ Please select at least one user before assigning an organization.");
            e.stopPropagation();
            e.preventDefault();
            return false;
        }

        selectedUsersInput.value = JSON.stringify(selectedUserIds);
        console.log("Selected Users Input Value:", selectedUsersInput.value);
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

    const selectAllCheckbox = document.getElementById("select-all-employer-checkbox");
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            const checkboxes = document.querySelectorAll(".employer-checkbox");
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
});

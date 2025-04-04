document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-user-btn");
    const editUserForm = document.getElementById("editUserForm");
  
    // Attach click event to each edit button
    editButtons.forEach(button => {
      button.addEventListener("click", function () {
        const curp = this.getAttribute("data-curp") || "";
        const firstName = this.getAttribute("data-first-name") || "";
        const lastName = this.getAttribute("data-last-name") || "";
        const email = this.getAttribute("data-email") || "";
        const isActive = this.getAttribute("data-is-active") || "";
        const role = this.getAttribute("data-role") || "";
        const language = this.getAttribute("data-language") || "";
  
        // Populate modal fields dynamically
        document.getElementById("edit_curp").value = curp;
        document.getElementById("edit_first_name").value = firstName;
        document.getElementById("edit_last_name").value = lastName;
        document.getElementById("edit_email").value = email;
        document.getElementById("edit_is_active").value = isActive;
        document.getElementById("edit_role").value = role;
        document.getElementById("edit_language").value = language;
  
        // Dynamically update form action URL
        if (editUserForm) {
          editUserForm.action = editUserForm.action.replace("curp_placeholder", curp);
        }
      });
    });
  
    // Handle form submission via AJAX
    if (editUserForm) {
      editUserForm.addEventListener("submit", function (event) {
        event.preventDefault();
  
        const formData = new FormData(editUserForm);
  
        fetch(editUserForm.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Hide the modal
            const modalElement = document.getElementById("editUserModal");
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
              modalInstance.hide();
            }
  
            // Refresh the page or update UI dynamically
            if (data.redirect_url) {
              window.location.href = data.redirect_url;
            } else {
              location.reload(); // Refresh the page to reflect changes
            }
          } else {
            alert("Error: " + (data.error || "Something went wrong"));
          }
        })
        .catch(error => console.error("Error:", error));
      });
    }
  });
  
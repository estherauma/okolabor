document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-user-btn");
    const editUserForm = document.getElementById("editWorkerForm");
  
    // Store the original action URL (once)
    if (editUserForm && !editUserForm.dataset.originalAction) {
      editUserForm.dataset.originalAction = editUserForm.action;
    }
  
    // Attach click event to each edit button
    editButtons.forEach(button => {
      button.addEventListener("click", function () {
        const curp = this.getAttribute("data-curp") || "";
        const firstName = this.getAttribute("data-first-name") || "";
        const lastName = this.getAttribute("data-last-name") || "";
        const email = this.getAttribute("data-email") || "";
        const isActive = this.getAttribute("data-is-active") || "";
          
  
        // Populate modal fields dynamically
        document.getElementById("edit_curp").value = curp;
        document.getElementById("edit_first_name").value = firstName;
        document.getElementById("edit_last_name").value = lastName;
        document.getElementById("edit_email").value = email;
        document.getElementById("edit_is_active").value = isActive;


        
        // Select correct value in dropdown
        const statusSelect = document.getElementById("edit_is_active");
        if (statusSelect) {
          [...statusSelect.options].forEach(opt => {
            opt.selected = opt.value === isActive;
          });
        }
  
        // Dynamically update form action URL
        if (editUserForm) {
          editUserForm.action = editUserForm.dataset.originalAction.replace("curp_placeholder", curp);
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
              const modalElement = document.getElementById("editWorkerModal");
              const modalInstance = bootstrap.Modal.getInstance(modalElement);
              if (modalInstance) {
                modalInstance.hide();
              }
  
              // Refresh the page or redirect
              if (data.redirect_url) {
                window.location.href = data.redirect_url;
              } else {
                location.reload(); // Refresh to reflect changes
              }
            } else {
              alert("Error: " + (data.error || "Something went wrong"));
            }
          })
          .catch(error => console.error("Error:", error));
      });
    }
  });
  
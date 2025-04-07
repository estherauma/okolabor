document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll(".edit-recruiter-btn");
  const editUserForm = document.getElementById("editRecruiterForm");

  editButtons.forEach(button => {
    button.addEventListener("click", function () {
      const curp = this.getAttribute("data-recruiter-curp") || "";
      const firstName = this.getAttribute("data-recruiter-first-name") || "";
      const lastName = this.getAttribute("data-recruiter-last-name") || "";
      const email = this.getAttribute("data-recruiter-email") || "";
      const isActive = this.getAttribute("data-recruiter-is-active") || "";
      const language = this.getAttribute("data-recruiter-language") || ""

      document.getElementById("edit_recruiter_curp").value = curp;
      document.getElementById("edit_recruiter_first_name").value = firstName;
      document.getElementById("edit_recruiter_last_name").value = lastName;
      document.getElementById("edit_recruiter_email").value = email;
      document.getElementById("edit_recruiter_is_active").value = isActive;
      document.getElementById("edit_recruiter_language").value = language;

      if (editUserForm) {
        editUserForm.action = editUserForm.action.replace("curp_placeholder", curp);
      }
    });
  });

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
          const modalElement = document.getElementById("editRecruiterModal");
          const modalInstance = bootstrap.Modal.getInstance(modalElement);
          if (modalInstance) {
            modalInstance.hide();
          }

          if (data.redirect_url) {
            window.location.href = data.redirect_url;
          } else {
            location.reload();
          }
        } else {
          alert("Error: " + (data.error || "Something went wrong"));
        }
      })
      .catch(error => console.error("Error:", error));
    });
  }
});

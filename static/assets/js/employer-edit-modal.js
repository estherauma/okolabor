document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll(".edit-employer-btn");
  const editEmployerForm = document.getElementById("editEmployerForm");

  editButtons.forEach(button => {
      button.addEventListener("click", function () {
          const curp = this.getAttribute("data-employer-curp") || "";
          const firstName = this.getAttribute("data-employer-first-name") || "";
          const lastName = this.getAttribute("data-employer-last-name") || "";
          const email = this.getAttribute("data-employer-email") || "";
          const isActive = this.getAttribute("data-employer-is-active") || "";
          const language = this.getAttribute("data-employer-language") || "";
          const group = this.getAttribute("data-employer-group") || "";

          document.getElementById("edit_employer_curp").value = curp;
          document.getElementById("edit_employer_first_name").value = firstName;
          document.getElementById("edit_employer_last_name").value = lastName;
          document.getElementById("edit_employer_email").value = email;
          document.getElementById("edit_employer_is_active").checked = (isActive === "True" || isActive === "true");
          document.getElementById("edit_employer_language").value = language;
          document.getElementById("edit_employer_group").value = group;

          // Optional: update the form action if needed
          if (editEmployerForm) {
              const originalAction = editEmployerForm.getAttribute("data-base-action");
              if (originalAction) {
                  editEmployerForm.action = originalAction.replace("curp_placeholder", curp);
              }
          }
      });
  });

  if (editEmployerForm) {
      editEmployerForm.addEventListener("submit", function (event) {
          event.preventDefault();
          const formData = new FormData(editEmployerForm);

          fetch(editEmployerForm.action, {
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
                  const modalElement = document.getElementById("editEmployerModal");
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

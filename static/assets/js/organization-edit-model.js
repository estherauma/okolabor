document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-organization-btn");
    const editOrganizationForm = document.getElementById("editOrganizationForm");
  
    editButtons.forEach(button => {
      button.addEventListener("click", function () {
        const organizationId = this.getAttribute("data-organization-id") || "";
        const name = this.getAttribute("data-organization-name") || "";
        const email = this.getAttribute("data-organization-email") || "";
        const phone = this.getAttribute("data-organization-phone") || "";
        const website = this.getAttribute("data-organization-website") || "";
        const address = this.getAttribute("data-organization-address") || "";
        const city = this.getAttribute("data-organization-city") || "";
        const state = this.getAttribute("data-organization-state") || "";
        const country = this.getAttribute("data-organization-country") || "";
        const zipCode = this.getAttribute("data-organization-zipcode") || "";
        const type = this.getAttribute("data-organization-type") || "";
        const isActive = this.getAttribute("data-organization-isactive") || "";
  
        document.getElementById("edit_organization_name").value = name;
        document.getElementById("edit_organization_email").value = email;
        document.getElementById("edit_organization_phone").value = phone;
        document.getElementById("edit_organization_website").value = website;
        document.getElementById("edit_organization_address").value = address;
        document.getElementById("edit_organization_city").value = city;
        document.getElementById("edit_organization_state").value = state;
        document.getElementById("edit_organization_country").value = country;
        document.getElementById("edit_organization_zip_code").value = zipCode;
        document.getElementById("edit_organization_type").value = type;
        document.getElementById("edit_organization_is_active").value = isActive;
  
        if (editOrganizationForm) {
          editOrganizationForm.action = editOrganizationForm.action.replace("organization_id_placeholder", organizationId);
        }
      });
    });
  
    if (editOrganizationForm) {
      editOrganizationForm.addEventListener("submit", function (event) {
        event.preventDefault();
  
        const formData = new FormData(editOrganizationForm);
  
        fetch(editOrganizationForm.action, {
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
            const modalElement = document.getElementById("editOrganizationModal");
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
  
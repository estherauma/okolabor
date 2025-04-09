document.addEventListener("DOMContentLoaded", function () {
  const sectorField = document.getElementById("id_type_sector");

  const toggleFields = () => {
    const value = sectorField.value;
    const show = (id) => document.getElementById(`div_${id}`).style.display = "block";
    const hide = (id) => document.getElementById(`div_${id}`).style.display = "none";

    const allFields = [
      "id_animal_types", "id_animal_jobs",
      "id_crop_types", "id_crop_jobs",
      "id_mechanic_jobs", "id_supervision_jobs",
      "id_description"
    ];
    allFields.forEach(hide);

    switch (value) {
      case "animals":
        show("id_animal_types");
        show("id_animal_jobs");
        show("id_description");
        break;
      case "construction":
      case "licensed_vehicle_operation":
      case "other":
        show("id_description");
        break;
      case "crop_horticulture":
        show("id_crop_types");
        show("id_crop_jobs");
        show("id_description");
        break;
      case "mechanics":
        show("id_mechanic_jobs");
        show("id_description");
        break;
      case "worker_supervision":
        show("id_supervision_jobs");
        show("id_description");
        break;
    }
  };

  if (sectorField) {
    sectorField.addEventListener("change", toggleFields);
    toggleFields(); // Initial call
  }

  // === Date Validation Logic ===
  const startDateInput = document.getElementById("id_start_date");
  const endDateInput = document.getElementById("id_end_date");

  function validateDates() {
    const start = new Date(startDateInput.value);
    const end = new Date(endDateInput.value);
    const errorMsgId = "date-error-msg";

    // Remove old error
    const oldError = document.getElementById(errorMsgId);
    if (oldError) oldError.remove();

    if (startDateInput.value && endDateInput.value && start > end) {
      const error = document.createElement("div");
      error.id = errorMsgId;
      error.className = "text-danger mt-2";
      error.innerText = "End date cannot be earlier than start date.";
      endDateInput.parentElement.appendChild(error);
    }
  }

  if (startDateInput && endDateInput) {
    startDateInput.addEventListener("change", validateDates);
    endDateInput.addEventListener("change", validateDates);
  }
});

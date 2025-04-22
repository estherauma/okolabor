document.addEventListener("DOMContentLoaded", function () {
  const sectorField = document.getElementById("id_type_sector");

  const toggleFields = () => {
    const value = sectorField.value.trim();

    const show = (id) => {
      const el = document.getElementById(`div_${id}`);
      if (el) el.style.display = "block";
    };

    const hide = (id) => {
      const el = document.getElementById(`div_${id}`);
      if (el) el.style.display = "none";
    };

    const allFields = [
      "id_animal_types",
      "id_animal_jobs",
      "id_crop_types",
      "id_crop_jobs",
      "id_mechanic_jobs",
      "id_supervision_jobs",
      "id_description"
    ];
    allFields.forEach(hide);

    if (value === "crop_and_horticulture") {
      show("id_crop_types");
      show("id_crop_jobs");
      show("id_description");
    } else if (value === "construction" || value === "licensed_vehicle_operation" || value === "other") {
      show("id_description");
    } else if (value === "animals") {
      show("id_animal_types");
      show("id_animal_jobs");
      show("id_description");
    } else if (value === "mechanics") {
      show("id_mechanic_jobs");
      show("id_description");
    } else if (value === "worker_supervision__management") {
      show("id_supervision_jobs");
      show("id_description");
    }
  };

  if (sectorField) {
    sectorField.addEventListener("change", toggleFields);
    toggleFields();
  }


  const startDateInput = document.getElementById("id_start_date");
  const endDateInput = document.getElementById("id_end_date");

  function validateDates() {
    const start = new Date(startDateInput.value);
    const end = new Date(endDateInput.value);
    const errorMsgId = "date-error-msg";

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

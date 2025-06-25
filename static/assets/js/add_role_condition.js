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
});

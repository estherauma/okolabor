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
  
    sectorField.addEventListener("change", toggleFields);
    toggleFields();
  });
  
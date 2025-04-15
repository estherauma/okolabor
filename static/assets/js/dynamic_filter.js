function addAnotherExperience() {
    const template = document.getElementById("form-template").innerHTML;
    const container = document.getElementById("filter-inputs-container");
    container.insertAdjacentHTML("beforeend", template);
    bindDynamicFieldEvents();

    const newForm = container.lastElementChild;
    const typeSectorSelect = newForm.querySelector('select[id$="id_type_sector"]');
    if (typeSectorSelect && typeSectorSelect.value) {
        typeSectorSelect.dispatchEvent(new Event('change'));
    }
}

function removeForm(button) {
    const form = button.closest(".job-experience-form");
    form.remove();
}

function bindDynamicFieldEvents() {
    const allTypeSelectors = document.querySelectorAll('select[id$="id_type_sector"]');

    allTypeSelectors.forEach(selector => {
        selector.removeEventListener('change', handleTypeSectorChange);
        selector.addEventListener('change', handleTypeSectorChange);
    });
}

function handleTypeSectorChange(event) {
    const typeSelector = event.target;
    const form = typeSelector.closest(".job-experience-form");

    const dynamicField1 = form.querySelector('select[id$="id_dynamic_field_1"]');
    const dynamicField2 = form.querySelector('select[id$="id_dynamic_field_2"]');

    const field1Label = form.querySelector('label[for$="id_dynamic_field_1"]');
    const field2Label = form.querySelector('label[for$="id_dynamic_field_2"]');

    const type = typeSelector.value;

    const fieldData = {
        "Animals": {
            field1Label: "Animal Type",
            field1Options: ["Asses", "Bees", "Buffalo"],
            field2Label: "Tasks",
            field2Options: ["Breeding", "Caring", "Packaging"]
        },
        "Crop and Horticulture": {
            field1Label: "Crop Type",
            field1Options: ["Avocados", "Bananas", "Brazil nuts"],
            field2Label: "Tasks",
            field2Options: ["Cultivating", "Grading and sorting", "Harvesting", "Other"]
        },
        "Mechanics": {
            field1Label: "Tasks",
            field1Options: ["Car", "Agricultural Equipment/Machinery"],
            field2Label: null,
            field2Options: null
        },
        "Worker Supervision/Management": {
            field1Label: "Tasks",
            field1Options: ["Animals", "Crop and Horticulture", "Other"],
            field2Label: null,
            field2Options: null
        }
    };

    const selected = fieldData[type];

    if (selected) {
        // Update Field 1
        field1Label.textContent = selected.field1Label;
        dynamicField1.innerHTML = `<option value="">Select ${selected.field1Label}</option>`;
        selected.field1Options.forEach(option => {
            dynamicField1.innerHTML += `<option value="${option}">${option}</option>`;
        });
        dynamicField1.parentElement.style.display = 'block';

        // Update Field 2
        if (selected.field2Options) {
            field2Label.textContent = selected.field2Label;
            dynamicField2.innerHTML = `<option value="">Select ${selected.field2Label}</option>`;
            selected.field2Options.forEach(option => {
                dynamicField2.innerHTML += `<option value="${option}">${option}</option>`;
            });
            dynamicField2.parentElement.style.display = 'block';
        } else {
            dynamicField2.innerHTML = "";
            dynamicField2.parentElement.style.display = 'none';
        }
    } else {
        dynamicField1.innerHTML = "";
        dynamicField2.innerHTML = "";
        dynamicField1.parentElement.style.display = 'none';
        dynamicField2.parentElement.style.display = 'none';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    bindDynamicFieldEvents();
    document.querySelectorAll('select[id$="id_type_sector"]').forEach(selector => {
        if (selector.value) {
            selector.dispatchEvent(new Event('change'));
        }
    });
});

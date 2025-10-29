let fieldData = {};

async function fetchFieldDataFromAPI() {
    try {
        const response = await fetch('/api/dynamic-field-data/');
        if (response.ok) {
            fieldData = await response.json();
        } else {
            console.error("Failed to fetch dynamic field data:", response.status);
        }
    } catch (error) {
        console.error("Error fetching dynamic field data:", error);
    }
}

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

    const dynamicSelectors = document.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]');
    dynamicSelectors.forEach(selector => {
        selector.parentElement.style.display = 'none';
        selector.style.display = 'none';  
    });
}

function handleTypeSectorChange(event) {
    const dynamicSelectors = document.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]');
    dynamicSelectors.forEach(selector => {
        selector.style.display = 'inline-block';  
        selector.removeEventListener('change', () => updatePills(selector));
        selector.addEventListener('change', () => updatePills(selector));
    });

    const typeSelector = event.target;
    const form = typeSelector.closest(".job-experience-form");

    const dynamicField1 = form.querySelector('select[id$="id_dynamic_field_1"]');
    const dynamicField2 = form.querySelector('select[id$="id_dynamic_field_2"]');

    const field1Label = form.querySelector('label[for$="id_dynamic_field_1"]');
    const field2Label = form.querySelector('label[for$="id_dynamic_field_2"]');

    const type = typeSelector.value;
    const selected = fieldData[type];

    if (selected) {
        field1Label.textContent = selected.field1Label;
        dynamicField1.innerHTML = "";
        dynamicField1.setAttribute("multiple", true);
        selected.field1Options.forEach(option => {
            dynamicField1.innerHTML += `<option value="${option}">${option}</option>`;
        });
        dynamicField1.parentElement.style.display = 'block';

        if (selected.field2Options) {
            field2Label.textContent = selected.field2Label;
            dynamicField2.innerHTML = "";
            dynamicField2.setAttribute("multiple", true);
            selected.field2Options.forEach(option => {
                dynamicField2.innerHTML += `<option value="${option}">${option}</option>`;
            });
            dynamicField2.parentElement.style.display = 'block';
        } else {
            dynamicField2.innerHTML = "";
            dynamicField2.removeAttribute("multiple");
            dynamicField2.parentElement.style.display = 'none';
        }
    } else {
        dynamicField1.innerHTML = "";
        dynamicField2.innerHTML = "";
        dynamicField1.removeAttribute("multiple");
        dynamicField2.removeAttribute("multiple");
        dynamicField1.parentElement.style.display = 'none';
        dynamicField2.parentElement.style.display = 'none';
    }

    updatePills(dynamicField1);
    updatePills(dynamicField2);
}

function updatePills(selectElement) {
    const formGroup = selectElement.closest(".form-group");
    let pillsContainer = formGroup.querySelector(".selected-options-container");

    if (!pillsContainer) {
        pillsContainer = document.createElement("div");
        pillsContainer.className = "selected-options-container";
        pillsContainer.style.marginTop = "0.5rem";
        pillsContainer.style.display = "none";
        formGroup.appendChild(pillsContainer);
    }

    const selectedOptions = Array.from(selectElement.selectedOptions).map(opt => opt.text).filter(Boolean);

    pillsContainer.innerHTML = "";
    selectedOptions.forEach(text => {
        const pill = document.createElement("span");
        pill.textContent = text;
        pill.style.display = "inline-block";
        pill.style.padding = "6px 14px";
        pill.style.margin = "4px 6px 4px 0";
        pill.style.fontSize = "0.9rem";
        pill.style.color = "#2d6a4f";
        pill.style.border = "1px solid #95d5b2";
        pill.style.borderRadius = "999px";
        pill.style.backgroundColor = "#f1fce9";
        pill.style.boxShadow = "0 1px 2px rgba(0, 0, 0, 0.05)";
        pillsContainer.appendChild(pill);
    });

    updateCollapseSummary();
}


document.addEventListener("DOMContentLoaded", async () => {
    await fetchFieldDataFromAPI();
    bindDynamicFieldEvents();

    document.querySelectorAll('select[id$="id_type_sector"]').forEach(selector => {
        if (selector.value) {
            selector.dispatchEvent(new Event('change'));
        }
    });

    document.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]').forEach(select => {
        updatePills(select);
    });

    updateCollapseSummary();
});

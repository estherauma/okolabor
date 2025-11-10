let fieldData = {};

function addAnotherExperience() {
    const template = document.getElementById("form-template").innerHTML;
    const container = document.getElementById("filter-inputs-container");
    container.insertAdjacentHTML("beforeend", template);

    const newForm = container.lastElementChild;
    const typeSectorSelect = newForm.querySelector('select[id$="id_type_sector"]');
    if (typeSectorSelect && typeSectorSelect.value) {
        typeSectorSelect.value = "";
        bindDynamicFieldEvents(newForm);
    }
}

function removeForm(button) {
    const form = button.closest(".job-experience-form");
    form.remove();
}

function bindDynamicFieldEvents(formEl) {
    const root = formEl || document;

    const allTypeSelectors = root.querySelectorAll('select[id$="id_type_sector"]');
    allTypeSelectors.forEach(selector => {
        selector.removeEventListener('change', handleTypeSectorChange);
        selector.addEventListener('change', handleTypeSectorChange);
    });

    const dynamicSelectors = root.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]');
    dynamicSelectors.forEach(selector => {
        selector.parentElement.style.display = 'none';
        selector.style.display = 'none';  
    });
}

function handleTypeSectorChange(event) {
    const typeSelector = event.target;
    const form = typeSelector.closest(".job-experience-form");
    const dynamicSelectors = form.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]');
    dynamicSelectors.forEach(selector => {
        selector.style.display = 'inline-block';  
        selector.removeEventListener('change', () => updatePills(selector));
        selector.addEventListener('change', () => updatePills(selector));
    });

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
function normalizeText(text) {
    return text.trim().toLowerCase().replace(/[\s\-\/]+/g, '_');
}
function toTitleCase(str) {
    return str.replace(/\w\S*/g, function(txt){
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}
function generateTextVariants(text) {
    const normalized = normalizeText(text);
    const variants = new Set();

    // Original and normalized
    variants.add(text);
    variants.add(normalized);

    // Lowercase, uppercase, title case
    variants.add(text.toLowerCase());
    variants.add(text.replace(/_/g, ' '));
    variants.add(text.replace(/ /g, '_'));
    variants.add(normalized.replace(/_/g, ' '));
    variants.add(normalized.replace(/ /g, '_'));

    // Title case for both original and normalized
    variants.add(toTitleCase(text.replace(/_/g, ' ')));
    variants.add(toTitleCase(normalized.replace(/_/g, ' ')));
    return Array.from(variants).filter(Boolean);
}

document.addEventListener("DOMContentLoaded", async () => {
    const expDynamicFieldData = localStorage.getItem('expDynamicFieldData');
    fieldData = expDynamicFieldData ? JSON.parse(expDynamicFieldData) : {};
    const params = new URLSearchParams(window.location.search);

    bindDynamicFieldEvents();

    document.querySelectorAll('select[id$="id_type_sector"]').forEach(selector => {
        if (selector.value) {
            selector.dispatchEvent(new Event('change'));
        }
    });

    document.querySelectorAll('select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]').forEach(select => {
        const values = params.getAll(select.name);
        if (values.length > 0) {
            const normalizedValues = values.map(normalizeText);

            console.log("Values Variants:", normalizedValues, values);
            Array.from(select.options).forEach(option => {
                const optionNormalized = normalizeText(option.value);
                console.log('option', option.value, optionNormalized, normalizedValues.includes(optionNormalized));

    option.selected = normalizedValues.includes(optionNormalized);
            });
        }
        updatePills(select);
    });

    updateCollapseSummary();
});

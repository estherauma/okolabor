$(document).ready(function () {
  (async function () {
    try {
      const response = await fetch('/api/dynamic-field-data/');
      if (response.ok) {
        const fieldData = await response.json();
        localStorage.setItem('expDynamicFieldData', JSON.stringify(fieldData));
      } else {
        console.error('Failed to fetch dynamic field data:', response.status);
      }
    } catch (error) {
      console.error('Error fetching dynamic field data:', error);
    }
    await initialize();
  })();
});

async function initialize() {
  const workRequestSelect = $('#modal_work_request');
  const roleSelect = $('#modal_role');

  // Initialize select2
  workRequestSelect.select2({
    placeholder: workRequestSelect.data('placeholder'),
    allowClear: true,
    minimumResultsForSearch: 0,
  });

  roleSelect.select2({
    placeholder: roleSelect.data('placeholder'),
    allowClear: true,
    minimumResultsForSearch: 0,
  });

  const tabToTableMap = {
    tab1: { tableId: 'basic-datatable-allworkers-workers', status: 'all' },
    tab2: { tableId: '#basic-datatable-shortlist', status: 'assigned' },
    tab3: { tableId: '#basic-datatable-offersent', status: 'offersent' },
    tab4: { tableId: '#basic-datatable-confirmed', status: 'confirmed' },
    tab5: { tableId: '#basic-datatable-rejectedTab5', status: 'rejected' },
  };

  $('a[data-bs-toggle="tab"]').on('shown.bs.tab', async function (e) {
    const activeTabId = $(e.target).attr('href').replace('#', '');
    sessionStorage.setItem('activeTabId', activeTabId);
    const _savedWorkRequest = sessionStorage.getItem('selectedWorkRequest');
    const _savedRole = sessionStorage.getItem('selectedRole');
    if (_savedWorkRequest && _savedRole) {
      if (activeTabId === 'tab1') {
        await handleAllWorkerTabFiltering({
          workRequestId: _savedWorkRequest,
          roleId: _savedRole,
        });
      } else {
        await handleOtherTabsFiltering({
          workRequestId: _savedWorkRequest,
          roleId: _savedRole,
          activeTabId,
          tabToTableMap,
        });
      }
    }
  });

  workRequestSelect.on('change', function () {
    const workRequestId = $(this).val();
    const params = new URLSearchParams(window.location.search);
    const hasRoleParam = params.has('role');
    const hasWorkRequestParam = params.has('work_request');

    if (!workRequestId) {
      sessionStorage.removeItem('selectedRole');
      sessionStorage.removeItem('selectedWorkRequest');
      if (
        (hasRoleParam || hasWorkRequestParam) &&
        window.location.pathname === '/workers/'
      ) {
        window.location.href = '/workers/';
      }
      return;
    }
    roleSelect.html(
      '<option value="">{% translate "workersListSelectARole" %}</option>'
    );

    if (workRequestId) {
      fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
        .then((response) => {
          if (!response.ok) throw new Error('Failed to load roles');
          return response.json();
        })
        .then((data) => {
          const sortedRoles = data.roles.sort((a, b) =>
            a.title.localeCompare(b.title, undefined, { sensitivity: 'base' })
          );
          sortedRoles.forEach((role) => {
            const option = $('<option></option>').val(role.id).text(role.title);
            roleSelect.append(option);
          });
        })
        .catch((error) => console.error('Error fetching roles:', error));
    }
  });

  roleSelect.on('change', async function () {
    const workRequestId = workRequestSelect.val();
    const roleId = roleSelect.val();
    const params = new URLSearchParams(window.location.search);
    const hasRoleParam = params.has('role');
    const hasWorkRequestParam = params.has('work_request');

    sessionStorage.setItem('selectedWorkRequest', workRequestId);
    sessionStorage.setItem('selectedRole', roleId);

    const activeTabId = $('.tab-pane.active').attr('id');
    const tabInfo = tabToTableMap[activeTabId];

    if (!tabInfo) return;

    const { tableId, status } = tabInfo;
    if (!roleId) {
      sessionStorage.removeItem('selectedRole');
      sessionStorage.removeItem('selectedWorkRequest');

      if (
        (hasRoleParam || hasWorkRequestParam) &&
        window.location.pathname === '/workers/'
      ) {
        window.location.href = '/workers/';
      }
      return;
    }

    await handleAllWorkerTabFiltering({ workRequestId, roleId });
    if (workRequestId && roleId && status === 'all') {
      await handleOtherTabsFiltering({
        workRequestId: workRequestId,
        roleId: roleId,
        activeTabId: 'tab2',
        tabToTableMap,
      });
    } else if (workRequestId && roleId) {
      await handleOtherTabsFiltering({
        workRequestId,
        roleId,
        activeTabId,
        tabToTableMap,
      });
    }
  });

  const savedWorkRequest = sessionStorage.getItem('selectedWorkRequest');
  const savedRole = sessionStorage.getItem('selectedRole');
  const savedTabId = sessionStorage.getItem('activeTabId');

  if (savedTabId) {
    $(`#${savedTabId}-tab`).tab('show');
  }

  if (savedWorkRequest) {
    workRequestSelect.val(savedWorkRequest).trigger('change');

    fetch(`/workers/get-roles-for-work-request/${savedWorkRequest}/`)
      .then((response) => response.json())
      .then((data) => {
        roleSelect.html(
          '<option value="">{% translate "workersListSelectARole" %}</option>'
        );
        data.roles.forEach((role) => {
          const option = $('<option></option>').val(role.id).text(role.title);
          roleSelect.append(option);
        });

        if (savedRole) {
          roleSelect.val(savedRole).trigger('change');
        }
      })
      .catch((error) =>
        console.error('Error restoring previous roles:', error)
      );
  }
}

// ✅ Select All Checkbox logic per tab
function bindSelectAllCheckbox(tabId) {
  let selectAllId = '';
  let checkboxClass = '';

  if (tabId === 'tab2') {
    selectAllId = '#select-all-shortlist';
    checkboxClass = '.worker-shortlist-checkbox';
  } else if (tabId === 'tab3') {
    selectAllId = '#select-all-offersent';
    checkboxClass = '.worker-offersent-checkbox';
  } else if (tabId === 'tab4') {
    selectAllId = '#select-all-confirmed';
    checkboxClass = '.worker-confirmed-checkbox';
  } else if (tabId === 'tab5') {
    selectAllId = '#select-all-rejected';
    checkboxClass = '.worker-rejected-checkbox';
  } else {
    return;
  }

  $(selectAllId)
    .off('change')
    .on('change', function () {
      const isChecked = $(this).is(':checked');
      $(checkboxClass).prop('checked', isChecked);
    });

  $(document)
    .off('change', checkboxClass)
    .on('change', checkboxClass, function () {
      const total = $(checkboxClass).length;
      const checked = $(checkboxClass + ':checked').length;
      $(selectAllId).prop('checked', total === checked);
    });
}

async function handleOtherTabsFiltering({
  workRequestId,
  roleId,
  activeTabId,
  tabToTableMap,
}) {
  try {
    const tabInfo = tabToTableMap[activeTabId];
    const { tableId, status } = tabInfo;

    const response = await fetch(
      `/workers/ajax-filtered-workers/?work_request=${workRequestId}&role=${roleId}&status=${status}`
    );
    if (!response?.ok) {
      throw new Error(`Failed to load role data ${response.status}`);
    }
    const data = await response.json();
    const counts = data.counts || {};
    const countIdMap = {
      assigned: '#shortlisted-count',
      offersent: '#offersent-count',
      confirmed: '#confirmed-count',
      rejected: '#rejected-count',
    };

    for (const item in counts) {
      $(countIdMap[item]).text(`(${counts[item]})`);
    }

    if (!$.fn.DataTable.isDataTable(tableId)) {
      $(tableId).DataTable({
        ordering: true,
        order: [],
        columnDefs: [
          { targets: 0, orderable: false },
          { targets: -1, orderable: false },
        ],
        paging: true,
        info: true,
      });
    }

    const table = $(tableId).DataTable({
      ordering: true,
      order: [],
      columnDefs: [
        { targets: 0, orderable: false },
        { targets: -1, orderable: false },
      ],
      paging: true,
      info: true,
    });
    table.clear();

    if (data.workers.length === 0) {
      table.row.add(['', 'No workers found', '', '', '', '', '', '', '', '']);
    } else {
      data.workers.forEach((worker) => {
        const tabCheckboxClassMap = {
          tab2: 'worker-shortlist-checkbox',
          tab3: 'worker-offersent-checkbox',
          tab4: 'worker-confirmed-checkbox',
          tab5: 'worker-rejected-checkbox',
        };
        const checkboxClass =
          tabCheckboxClassMap[activeTabId] || 'worker-default-checkbox';
        table.row.add([
          `<input type="checkbox" name="${checkboxClass}" class="${checkboxClass}" value="${worker.id}" data-worker-name="${worker.name}">`,
          `<a href="${worker.id}">${worker.name}</a>`,
          worker.relExp,
          worker.h2aExp,
          worker.offer,
          worker.profile,
          worker.visa,
        ]);
      });
    }

    table.draw();
    bindSelectAllCheckbox(activeTabId);
  } catch (error) {
    console.error('Error fetching role data:', error);
  }
}

async function handleAllWorkerTabFiltering({ workRequestId, roleId }) {
  const dynamic_fields_keys = {
    animals: {
      type_details_key: 'animal_types',
      responsibilities_key: 'responsibilities_types',
      dbValue: 'Animals',
    },
    crop_and_horticulture: {
      type_details_key: 'crop_types',
      responsibilities_key: 'crop_job_types',
      dbValue: 'Crop and Horticulture',
    },
    mechanics: {
      responsibilities_key: 'mechanic_job_types',
      dbValue: 'Mechanics',
    },
    worker_supervision: {
      responsibilities_key: 'supervision_jobs_types',
      dbValue: 'Worker Supervision/Management',
    },
    licensed_vehicle_operation: {
      responsibilities_key: 'licensed_vehicle_operation_types',
      dbValue: 'Licensed Vehicle Operation',
    },
    other: {
      dbValue: 'Other',
    },
  };
  if (!workRequestId || !roleId) return;
  try {
    const response = await fetch(`/roles/${roleId}/`);
    if (!response?.ok) {
      throw new Error(`Failed to load role data ${response.status}`);
    }

    const roleRespData = await response.json();
    const role = roleRespData.role;
    let type_sector_keys = dynamic_fields_keys[role.work_type];
    let typeSectorDetails = [];
    let typeSectorResponsibilities = [];

    if (!type_sector_keys) {
      type_sector_keys = dynamic_fields_keys.other;
    }
    let url = `/workers/?work_request=${workRequestId}&role=${roleId}&type_sector=${type_sector_keys?.dbValue}`;

    if (role.work_type_detail) {
      let details_key = type_sector_keys['type_details_key'];
      let responsibilities_key = type_sector_keys['responsibilities_key'];

      typeSectorDetails = role.work_type_detail[details_key] || [];
      typeSectorResponsibilities = responsibilities_key
        ? role.work_type_detail[responsibilities_key] || []
        : [];
    }

    if (typeSectorDetails.length > 0) {
      const detailsParams = typeSectorDetails
        .map((detail) => `dynamic_field_1=${encodeURIComponent(detail)}`)
        .join('&');
      url += `&${detailsParams}`;
    }
    if (typeSectorResponsibilities.length > 0) {
      const responsibilitiesParams = typeSectorResponsibilities
        .map(
          (responsibility) =>
            `dynamic_field_2=${encodeURIComponent(responsibility)}`
        )
        .join('&');
      url += `&${responsibilitiesParams}`;
    }
    const workersResponse = await fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    });
    if (!workersResponse?.ok) {
      throw new Error(`Failed to fetch workers ${workersResponse.status}`);
    }
    const workersResponseData = await workersResponse.json();
    document.getElementById(
      'all-workers-count'
    ).textContent = `(${workersResponseData.workers.length})`;
    console.log('Filtered workers for All tab:', workersResponseData);
    const tableId = '#basic-datatable-allworkers-workers';
    console.log('Updating URL to:', url);
    window.history.replaceState({}, '', url);
    
    // Update the type sector select element
    const type_sector_select = document.querySelector(
      'select[id$="id_type_sector"]'
    );
    if (type_sector_select) {
      type_sector_select.value = type_sector_keys.dbValue;
      type_sector_select.dispatchEvent(new Event('change'));
    }
    document
      .querySelectorAll(
        'select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"]'
      )
      .forEach((select) => {
        const _values =
          select.name === 'dynamic_field_1'
            ? typeSectorDetails
            : typeSectorResponsibilities;
        if (_values.length) {
          const normalizedValues = _values.map(normalizeText);
          Array.from(select.options).forEach((option) => {
            const optionNormalized = normalizeText(option.value);
            option.selected = normalizedValues.includes(optionNormalized);
          });
        }
    });

    updateCollapseSummary();
    if (!$.fn.DataTable.isDataTable(tableId)) {
      $(tableId).DataTable({
        ordering: true,
        order: [],
        columnDefs: [
          { targets: 0, orderable: false },
          { targets: -1, orderable: false },
        ],
        paging: true,
        info: true,
      });
    }

    const table = $(tableId).DataTable();
    table.clear();

    if (workersResponseData.workers.length === 0) {
      table.row.add(['', 'No workers found', '', '', '', '', '', '', '', '']);
    } else {
      workersResponseData.workers.forEach((worker) => {
        const name =
          worker.first_name || worker.last_name
            ? `${worker.first_name} ${worker.last_name}`
            : 'Not Provided';
        let actions = '';
        console.log('isAdmin value:', isAdmin);
        if (typeof isAdmin !== 'undefined' && isAdmin) {
          actions = `
                  <button type="button" class="btn btn-sm yellow-button" data-bs-toggle="modal"
                    data-bs-target="#editModal${worker.id}" title="Edit">
                    Edit
                  </button>
                  <button type="button" class="btn btn-sm red-button ms-2" data-bs-toggle="modal"
                    data-bs-target="#deleteModalWorker${worker.id}" title="Delete">
                    Delete
                  </button>
                `;
        }
        table.row.add([
          `<input type="checkbox"class="worker-checkbox" value="${worker.id}" data-worker-name="${name}">`,
          `<a href="${worker.id}">${name}</a>`,
          worker.years_of_experience ?? '',
          worker.total_months_of_h2a_experience ?? '',
          worker.latest_status ?? '',
          worker.profile_completion_percentage == 100 ? 'Yes' : 'No',
          worker.visa_uploaded ? 'Yes' : 'No',
          actions,
        ]);
      });
    }

    table.draw();
  } catch (error) {
    console.error('Error fetching dynamic field data:', error);
  }
}

function getSecondaryFiltersOptions() {
  const options = localStorage.getItem('secondaryFilterOptions');
  return options ? JSON.parse(options) : [];
}

function getMappedlocalizedFilterValues({ params }) {
  const randomFilterMapping = {};
  const secondaryFiltersOptions = getSecondaryFiltersOptions();

  for (const [key, value] of params.entries()) {
    if (key.includes('random_filter')) {
      randomFilterMapping[value] = {
        label:
          secondaryFiltersOptions?.find((opt) => opt.value === value)?.label ||
          value,
        value: value,
      };
      continue;
    }
    if (key.includes('age_min')) {
      let currentKeyValues = randomFilterMapping['age'];
      if (currentKeyValues) {
        currentKeyValues['age_min'] = value;
      } else {
        currentKeyValues['label'] =
          secondaryFiltersOptions?.find((opt) => opt.value === 'age')?.label ||
          'Age';
        currentKeyValues['age_min'] = value;
      }
      randomFilterMapping['age'] = currentKeyValues;
    } else if (key.includes('age_max')) {
      let currentKeyValues = randomFilterMapping['age'];
      if (currentKeyValues) {
        currentKeyValues['age_max'] = value;
      } else {
        currentKeyValues['label'] =
          secondaryFiltersOptions?.find((opt) => opt.value === 'age')?.label ||
          'Age';
        currentKeyValues['age_max'] = value;
      }
      randomFilterMapping['age'] = currentKeyValues;
    } else if (key.includes('availability_from')) {
      let currentKeyValues = randomFilterMapping['availability'];
      if (currentKeyValues) {
        currentKeyValues['availability_from'] = value;
      } else {
        currentKeyValues['label'] =
          secondaryFiltersOptions?.find((opt) => opt.value === 'availability')
            ?.label || 'Availability';
        currentKeyValues['availability_from'] = value;
      }
      randomFilterMapping['availability'] = currentKeyValues;
    } else if (key.includes('language_proficiency_level')) {
      let currentKeyValues = randomFilterMapping['language_proficiency'];
      if (currentKeyValues) {
        currentKeyValues['language_proficiency'] = value;
      } else {
        currentKeyValues = {
          label:
            secondaryFiltersOptions?.find(
              (opt) => opt.value === 'language_proficiency'
            )?.label || 'Language Proficiency',
          value: value,
        };
      }
      randomFilterMapping['language_proficiency'] = currentKeyValues;
    } else if (key.includes('language_video')) {
      let currentKeyValues = randomFilterMapping['language_proficiency'];
      if (currentKeyValues) {
        currentKeyValues['language_video'] = value;
      } else {
        currentKeyValues = {
          label:
            secondaryFiltersOptions?.find(
              (opt) => opt.value === 'language_proficiency'
            )?.label || 'Language Proficiency',
          value: 'language_proficiency',
          language_video: {
            value,
            label:
              secondaryFiltersOptions?.find(
                (opt) => opt.value === 'has_language_proficiency_video'
              )?.label || 'Language Video',
          },
        };
      }
      randomFilterMapping['language_proficiency'] = currentKeyValues;
    } else if (key.includes('years_of_experience_min')) {
      let currentKeyValues = randomFilterMapping['years_of_experience'];
      if (currentKeyValues) {
        currentKeyValues['years_of_experience'] = value;
      } else {
        currentKeyValues = {
          label:
            secondaryFiltersOptions?.find(
              (opt) => opt.value === 'years_of_experience'
            )?.label || 'Months of experience',
          value: value,
        };
      }
      randomFilterMapping['years_of_experience'] = currentKeyValues;
    } else if (/_\d+$/.test(key)) {
      const cleanedKey = key.replace(/_[^_]+$/, '');
      let currentKeyValues = randomFilterMapping['references'];
      if (currentKeyValues) {
        currentKeyValues[cleanedKey] = value;
      } else {
        currentKeyValues = {
          label:
            secondaryFiltersOptions?.find((opt) => opt.value === cleanedKey)
              ?.label || cleanedKey,
          value: value,
        };
      }
      randomFilterMapping[cleanedKey] = currentKeyValues;
    }
  }

  return randomFilterMapping;
}

function updateCollapseSummary() {
  const expDynamicFieldData = localStorage.getItem('expDynamicFieldData');
  const parsedDynamicFieldData = expDynamicFieldData
    ? JSON.parse(expDynamicFieldData)
    : {};
  const summaryContainer = document.getElementById('selected-filters-summary');
  summaryContainer.innerHTML = '';

  const allSelectedTextsSet = new Set();
  var collapseCard = document.getElementById('collapseCard');
  var toggleBtn = document.getElementById('toggle-sign-btn');

  if (collapseCard && toggleBtn) {
    collapseCard.addEventListener('show.bs.collapse', function () {
      toggleBtn.textContent = '–'; // Change to minus when expanded
    });
    collapseCard.addEventListener('hide.bs.collapse', function () {
      toggleBtn.textContent = '+'; // Change to plus when collapsed
    });
  }

  // ✅ 1. Extract filters from URL parameters
  const params = new URLSearchParams(window.location.search);
  const typeSectorValue = params.get('type_sector');
  let localizedTypeSectorData;
  if (typeSectorValue) {
    localizedTypeSectorData = parsedDynamicFieldData[typeSectorValue];
  }
  const randomFilterMapping = getMappedlocalizedFilterValues({ params });

  for (const [key, value] of params.entries()) {
    if (!value) continue;
    const cleanedKey = key.replace(/_[^_]+$/, '');
    let label = '';

    let formattedValue = decodeURIComponent(value.replace(/\+/g, ' '));
    if (key.includes('random_filter')) {
      continue;
    }

    if (key.includes('type_sector')) label = 'Type/Sector';
    else if (key.includes('dynamic_field_1')) {
      // Change label based on type_sector value
      let newValue =
        localizedTypeSectorData?.types?.find((item) => item.value === value)
          ?.label || value;
      if (typeSectorValue === 'Animals') {
        label = 'Animal Type';
      } else if (typeSectorValue === 'Crop and Horticulture') {
        label = 'Crop Type';
      } else {
        newValue =
          localizedTypeSectorData?.tasks?.find((item) => item.value === value)
            ?.label || value;
        label = 'Tasks';
      }
      formattedValue = decodeURIComponent(newValue.replace(/\+/g, ' '));
    } else if (key.includes('dynamic_field_2')) {
      label = 'Tasks';
      const newValue =
        localizedTypeSectorData?.tasks?.find((item) => item.value === value)
          ?.label || value;
      formattedValue = decodeURIComponent(newValue.replace(/\+/g, ' '));
    } else if (randomFilterMapping[cleanedKey]) {
      label = randomFilterMapping[cleanedKey]?.label || key;
    }

    // else if (key.includes('availability')){
    //     label = randomFilterMapping['availability']?.label || 'Availability';
    //     const from = params.get('availability_from') || '';
    //     const to = params.get('availability_to') || '';
    //     if (from && to) formattedValue = `${from} to ${to}`;
    //     else if (from) formattedValue = `From ${from}`;
    //     else if (to) formattedValue = `To ${to}`;
    // }
    else if (key.includes('language_proficiency_level')) {
      label = randomFilterMapping['language_proficiency']?.label;
    } else if (key.includes('language_video')) {
      label =
        randomFilterMapping['language_proficiency']?.language_video?.label ||
        'Language Video';
    } else if (key.includes('age_min') || key.includes('age_max')) {
      const _age = randomFilterMapping['age'];
      const min = _age.age_min || '';
      const max = _age.age_max || '';
      label = _age?.label || 'Age';
      if (min && max) formattedValue = `${min} - ${max}`;
      else if (min) formattedValue = `Min ${min}`;
      else if (max) formattedValue = `Max ${max}`;
    } else if (key.includes('years_of_experience_min')) {
      label =
        randomFilterMapping['years_of_experience']?.label ||
        'Months of experience';
    }
    if (!label) continue;
    allSelectedTextsSet.add(`${label}: ${formattedValue}`);
  }

  // ✅ 2.Extract filters from select elements
  const experienceSelects = document.querySelectorAll(
    'select[id$="id_dynamic_field_1"], select[id$="id_dynamic_field_2"], select[id$="id_type_sector"]'
  );
  experienceSelects.forEach((select) => {
    const selectedOptions = Array.from(select.selectedOptions)
      .map((opt) => opt.text.trim())
      .filter((text) => text && text !== 'Please select...');

    if (selectedOptions.length > 0) {
      let labelText = '';

      const fieldId = select.getAttribute('id');
      const labelEl = document.querySelector(`label[for="${fieldId}"]`);

      if (labelEl) {
        labelText = labelEl.textContent.trim().replace(':', '');
      } else {
        if (select.name.includes('type_sector')) labelText = 'Type';
        else if (select.name.includes('dynamic_field_1'))
          labelText = 'Animal Type';
        else if (select.name.includes('dynamic_field_2')) labelText = 'Tasks';
        else labelText = 'Filter';
      }
      allSelectedTextsSet.add(`${labelText}: ${selectedOptions.join(', ')}`);
    }
  });

  const randomFilterRows = document.querySelectorAll(
    '#dynamic-random-filters .filter-group'
  );
  randomFilterRows.forEach((row) => {
    const selectFilter = row.querySelector('select[name="random_filter"]');
    const filterLabel =
      selectFilter?.options[selectFilter.selectedIndex]?.text?.trim();
    if (!filterLabel || filterLabel === 'Choose a filter') return;

    let valueText = '';

    if (selectFilter.value === 'availability') {
      const fromInput = row.querySelector(`input[name^="availability_from_"]`);
      const toInput = row.querySelector(`input[name^="availability_to_"]`);
      const fromVal = fromInput?.value;
      const toVal = toInput?.value;
      if (fromVal && toVal) valueText = `${fromVal} to ${toVal}`;
      else if (fromVal) valueText = `From ${fromVal}`;
      else if (toVal) valueText = `To ${toVal}`;
    } else if (['age', 'years_of_experience'].includes(selectFilter.value)) {
      const minInput = row.querySelector(
        `input[name^="${selectFilter.value}_min_"]`
      );
      const maxInput = row.querySelector(
        `input[name^="${selectFilter.value}_max_"]`
      );
      const minVal = minInput?.value;
      const maxVal = maxInput?.value;
      if (minVal && maxVal) valueText = `${minVal} - ${maxVal}`;
      else if (minVal) valueText = `Min ${minVal}`;
      else if (maxVal) valueText = `Max ${maxVal}`;
      const selectsAndInputs = row.querySelectorAll(
        '.col-md-6 select, .col-md-6 input'
      );
      selectsAndInputs.forEach((input) => {
        if (input.tagName === 'SELECT') {
          const selectedOptions = Array.from(input.selectedOptions)
            .map((opt) => opt.text.trim())
            .filter((text) => text && text !== 'Please select...');
          if (selectedOptions.length > 0)
            valueText = selectedOptions.join(', ');
        } else if (input.tagName === 'INPUT') {
          const val = input.value.trim();
          if (val) valueText = val;
        }
      });
    }

    if (valueText) {
      allSelectedTextsSet.add(`${filterLabel}: ${valueText}`);
    }
  });

  // ✅ 3. Render pills without duplicates
  if (allSelectedTextsSet.size > 0) {
    const label = document.createElement('strong');
    label.textContent = 'Active filters: ';
    summaryContainer.appendChild(label);

    allSelectedTextsSet.forEach((text) => {
      const pill = document.createElement('span');
      pill.textContent = text;
      // If text starts with Role: or Work Request:, display none
      // This is to hide the role and wr from the pill as there's a form for them
      if (text.startsWith('Role:') || text.startsWith('Work Request:')) {
        pill.style.display = 'none';
      } else {
        pill.style.display = 'inline-block';
      }
      pill.style.padding = '4px 10px';
      pill.style.margin = '2px 4px';
      pill.style.fontSize = '0.75rem';
      pill.style.color = '#1b4332';
      pill.style.border = '1px solid #74c69d';
      pill.style.borderRadius = '999px';
      pill.style.backgroundColor = '#d8f3dc';
      pill.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
      summaryContainer.appendChild(pill);
    });
  }
}

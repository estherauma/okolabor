$(document).ready(function () {
    const workRequestSelect = $('#modal_work_request');
    const roleSelect = $('#modal_role');

    // Initialize select2
    workRequestSelect.select2({
        placeholder: roleSelect.data('placeholder'),
        allowClear: true,
        minimumResultsForSearch: 0
    });

    roleSelect.select2({
        placeholder: roleSelect.data('placeholder'),
        allowClear: true,
        minimumResultsForSearch: 0
    });

    const tabToTableMap = {
        tab2: { tableId: '#basic-datatable-shortlist', status: 'assigned' },
        tab3: { tableId: '#basic-datatable-offersent', status: 'offersent' },
        tab4: { tableId: '#basic-datatable-confirmed', status: 'confirmed' },
        tab5: { tableId: '#basic-datatable-rejectedTab5', status: 'rejected' },
    };

    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const activeTabId = $(e.target).attr('href').replace('#', '');
        sessionStorage.setItem("activeTabId", activeTabId);
        roleSelect.trigger('change');
    });

    workRequestSelect.on('change', function () {
        const workRequestId = $(this).val();
        roleSelect.html('<option value="">{% translate "workersListSelectARole" %}</option>');

        if (workRequestId) {
            fetch(`/workers/get-roles-for-work-request/${workRequestId}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load roles');
                    return response.json();
                })
                .then(data => {
                    const sortedRoles = data.roles.sort((a, b) => a.title.localeCompare(b.title, undefined, { sensitivity: 'base' }));
                    sortedRoles.forEach(role => {
                        const option = $('<option></option>')
                            .val(role.id)
                            .text(role.title);
                        roleSelect.append(option);
                    });
                })
                .catch(error => console.error('Error fetching roles:', error));
        }
    });

    roleSelect.on('change', function () {
        const workRequestId = workRequestSelect.val();
        const roleId = roleSelect.val();

        sessionStorage.setItem("selectedWorkRequest", workRequestId);
        sessionStorage.setItem("selectedRole", roleId);

        const activeTabId = $('.tab-pane.active').attr('id');
        const tabInfo = tabToTableMap[activeTabId];

        if (!tabInfo) return;

        const { tableId, status } = tabInfo;

        if (workRequestId && roleId) {
            fetch(`/workers/ajax-filtered-workers/?work_request=${workRequestId}&role=${roleId}&status=${status}`)
                .then(res => res.json())
                .then(data => {
                    const counts = data.counts || {};
                    const countIdMap = {
                        'assigned': '#shortlisted-count',
                        'offersent': '#offersent-count',
                        'confirmed': '#confirmed-count',
                        'rejected': '#rejected-count'
                    };

                    if (counts[status] !== undefined && countIdMap[status]) {
                        $(countIdMap[status]).text(`(${counts[status]})`);
                    }

                    if (!$.fn.DataTable.isDataTable(tableId)) {
                        $(tableId).DataTable({
                            ordering: true,
                            order: [],
                            columnDefs: [
                                { targets: 0, orderable: false },
                                { targets: -1, orderable: false }
                            ],
                            paging: true,
                            info: true
                        });
                    }

                    const table = $(tableId).DataTable();
                    table.clear();

                    if (data.workers.length === 0) {
                        table.row.add([
                            '', 'No workers found', '', '', '', '', '', '', '', ''
                        ]);
                    } else {
                        data.workers.forEach(worker => {
                            const tabCheckboxClassMap = {
                                tab2: 'worker-shortlist-checkbox',
                                tab3: 'worker-offersent-checkbox',
                                tab4: 'worker-confirmed-checkbox',
                                tab5: 'worker-rejected-checkbox',
                            };
                            const checkboxClass = tabCheckboxClassMap[activeTabId] || 'worker-default-checkbox';
                            table.row.add([
                                `<input type="checkbox" name="${checkboxClass}" class="${checkboxClass}" value="${worker.id}" data-worker-name="${worker.name}">`,
                                `<a href="${worker.id}">${worker.name}</a>`,
                                worker.town || 'Not Provided',
                                `${worker.profile_completion || 0}%`,
                                worker.experience || 'Not Provided',
                                worker.english_proficiency || 'Not Provided',
                                worker.location_preference || 'Not Provided',
                                worker.work_request || 'N/A',
                                worker.role || 'N/A',
                                worker.status || 'N/A'
                            ]);
                        });
                    }

                    table.draw();
                    bindSelectAllCheckbox(activeTabId); // ✅ Add this line
                })
                .catch(err => {
                    console.error('Error loading filtered workers:', err);
                });
        }
    });

    const savedWorkRequest = sessionStorage.getItem("selectedWorkRequest");
    const savedRole = sessionStorage.getItem("selectedRole");
    const savedTabId = sessionStorage.getItem("activeTabId");

    if (savedTabId) {
        $(`#${savedTabId}-tab`).tab('show');
    }

    if (savedWorkRequest) {
        workRequestSelect.val(savedWorkRequest).trigger('change');

        fetch(`/workers/get-roles-for-work-request/${savedWorkRequest}/`)
            .then(response => response.json())
            .then(data => {
                roleSelect.html('<option value="">{% translate "workersListSelectARole" %}</option>');
                data.roles.forEach(role => {
                    const option = $('<option></option>')
                        .val(role.id)
                        .text(role.title);
                    roleSelect.append(option);
                });

                if (savedRole) {
                    roleSelect.val(savedRole).trigger('change');
                }
            })
            .catch(error => console.error('Error restoring previous roles:', error));
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

        $(selectAllId).off('change').on('change', function () {
            const isChecked = $(this).is(':checked');
            $(checkboxClass).prop('checked', isChecked);
        });

        $(document).off('change', checkboxClass).on('change', checkboxClass, function () {
            const total = $(checkboxClass).length;
            const checked = $(checkboxClass + ':checked').length;
            $(selectAllId).prop('checked', total === checked);
        });
    }
});

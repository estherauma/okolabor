$(document).ready(function () {
    const workRequestSelect = $('#modal_work_request');
    const roleSelect = $('#modal_role');

    // Initialize Select2 for Work Request
    workRequestSelect.select2({
        placeholder: "Search for job orders...",
        width: '59%',
        allowClear: true,
        minimumResultsForSearch: 0
    });

    // Map tab IDs to their corresponding table IDs and status
    const tabToTableMap = {
        tab2: { tableId: '#basic-datatable-shortlist', status: 'assigned' },
        tab3: { tableId: '#basic-datatable-offersent', status: 'offersent' },
        tab4: { tableId: '#basic-datatable-confirmed', status: 'confirmed' },
        tab5: { tableId: '#basic-datatable-rejectedTab5', status: 'rejected' },
    };

    // Fetch roles when a Work Request is selected
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
                    data.roles.forEach(role => {
                        const option = $('<option></option>')
                            .val(role.id)
                            .text(role.title);
                        roleSelect.append(option);
                    });
                })
                .catch(error => console.error('Error fetching roles:', error));
        }
    });

    // Fetch filtered workers when a Role is selected
    roleSelect.on('change', function () {
        const workRequestId = workRequestSelect.val();
        const roleId = roleSelect.val();

        // Get active tab ID (tab2, tab3, etc.)
        const activeTabId = $('.tab-pane.active').attr('id');
        const tabInfo = tabToTableMap[activeTabId];

        console.log('Active Tab ID:', activeTabId);
        console.log('Tab Info:', tabInfo);

        if (!tabInfo) return;  // Skip if tab is not mapped

        const { tableId, status } = tabInfo;

        if (workRequestId && roleId) {
            console.log(`Fetching workers for Work Request ID: ${workRequestId}, Role ID: ${roleId}, Status: ${status}`);
            fetch(`/workers/ajax-filtered-workers/?work_request=${workRequestId}&role=${roleId}&status=${status}`)
                .then(res => res.json())
                .then(data => {
                    const tableBody = $(`${tableId} tbody`);
                    tableBody.empty();

                    console.log(data.workers.length,"length")

                    if (data.workers.length === 0) {
                        tableBody.append('<tr><td colspan="10" class="text-center">No workers found</td></tr>');
                    } else {
                        console.log('Filtered Workers:', data.workers);
                        data.workers.forEach(worker => {
                            const row = `
                                <tr class="text-center">
                                    <td><input type="checkbox" class="worker-shortlist-checkbox" value="${worker.id}" data-worker-name="${worker.name}"></td>
                                    <td class="col-name"><a href="${worker.id}">${worker.name}</a></td>
                                    <td class="col-town">${worker.town || 'Not Provided'}</td>
                                    <td class="col-profile">${worker.profile_completion || 0}%</td>
                                    <td class="col-experience">${worker.experience || 'Not Provided'}</td>
                                    <td class="col-english">${worker.english_proficiency || 'Not Provided'}</td>
                                    <td class="col-location">${worker.location_preference || 'Not Provided'}</td>
                                    <td class="col-location">${worker.work_request || 'N/A'}</td>
                                    <td class="col-location">${worker.role || 'N/A'}</td>
                                    <td class="col-offer">${worker.status || 'N/A'}</td>
                                </tr>
                            `;
                            tableBody.append(row);
                        });
                    }
                })
                .catch(err => {
                    console.error('Error loading filtered workers:', err);
                });
        }
    });
});

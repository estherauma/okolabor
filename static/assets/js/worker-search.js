document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('.search-input');
    const resultsTableBody = document.querySelector('#basic-datatable tbody');

    function updateAssignButtonState() {
        const assignButton = document.querySelector(".dark-green-button");
        const workerCheckboxes = document.querySelectorAll(".worker-checkbox");
        const isAnyChecked = Array.from(workerCheckboxes).some(checkbox => checkbox.checked);
        assignButton.disabled = !isAnyChecked; 
    }

    function attachCheckboxListeners() {
        const workerCheckboxes = document.querySelectorAll(".worker-checkbox");
        workerCheckboxes.forEach(checkbox => {
            checkbox.addEventListener("change", updateAssignButtonState);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = searchInput.value;

            fetch(`?search=${query}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    resultsTableBody.innerHTML = '';
                    data.workers.forEach(worker => {
                        const firstName = worker.firstname || 'N/A';
                        const lastName = worker.lastname || 'N/A';
                        const email = worker.email || 'N/A';
                        const profileCompletion = worker.profile_completion || '0';

                        const row = `
                            <tr class="text-center">
                                <td>
                                    <input type="checkbox" class="worker-checkbox" value="${worker.id}" data-worker-name="${firstName} ${lastName}">
                                </td>
                                <td>
                                    <a href="/${worker.id}">
                                        ${email}
                                    </a>
                                </td>
                                <td>Chloe</td>
                                <td>${profileCompletion}%</td>
                                <td>Harvesting Fruit Picking</td>
                                <td>Intermediate</td>
                                <td>Any</td>
                                <td>Pending</td>
                            </tr>
                        `;
                        resultsTableBody.insertAdjacentHTML('beforeend', row);
                    });

                    // Reattach event listeners after updating the table
                    attachCheckboxListeners();
                    updateAssignButtonState(); // Update button state after rendering new data
                });
        });
    }

    attachCheckboxListeners(); // Attach event listeners when the page loads
});

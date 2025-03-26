document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('.search-input');
    const resultsTableBody = document.querySelector('#basic-datatable tbody');

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
                    resultsTableBody.innerHTML = ''; // Clear existing results
                    data.workers.forEach(worker => {
                        const row = `
                            
                        `;
                        resultsTableBody.insertAdjacentHTML('beforeend', row);
                    });
                });
        });
    }
});

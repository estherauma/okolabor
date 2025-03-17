document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input');
  const employersTableBody = document.getElementById('employers-table-body');
  let timeout = null;

  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const query = searchInput.value;
      console.log('Input event triggered with query:', query);

      // Clear the previous timeout
      clearTimeout(timeout);

      // Set a new timeout to debounce the input
      timeout = setTimeout(() => {
        fetch(`?query=${query}`, {
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        .then(response => response.json())
        .then(data => {
          console.log('Data fetched:', data);
          employersTableBody.innerHTML = ''; // Clear existing results
          data.employers.forEach(employer => {
            const row = `
              <tr class="text-center">
                <td><input class="table-checkbox" type="checkbox"/></td>
                <td>${employer.name}</td>
                <td>${employer.email}</td>
                <td>${employer.address}</td>
                <td>${employer.country}</td>
                <td>${employer.phone}</td>
                <td>
                  <a class="btn btn-primary" href="/employers/${employer.id}">
                    <i class="fe fe-eye"></i> View
                  </a>
                </td>
              </tr>
            `;
            employersTableBody.insertAdjacentHTML('beforeend', row);
          });
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
      }, 100); // Adjust the debounce delay as needed
    });
  }
});

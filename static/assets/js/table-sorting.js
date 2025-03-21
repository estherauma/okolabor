$(document).ready(function () {
    $('#basic-datatable, #employers-datatable, #workrequest-datatable').DataTable({
        "ordering": true,
        "order": [], // Default ordering (no pre-sorting)
        "columnDefs": [{
            "targets": '_all',
            "orderable": true // Enables sorting on all columns
        }]
    });
});

$(document).ready(function () {
    $('#basic-datatable, #employers-list-datatable, #workrequest-datatable, #another-basic-datatable,').DataTable({
        "ordering": true,
        "order": [], // Default ordering (no pre-sorting)
        "columnDefs": [{
            "targets": '_all',
            "orderable": true // Enables sorting on all columns
        }],
        "paging": false, // Disable pagination
        "info": false, // Hide "Showing X to Y of Z entries"
    });
});

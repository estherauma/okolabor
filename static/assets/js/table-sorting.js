$(document).ready(function () {
    if ($.fn.DataTable) {
        // Tables with common settings
        $('#basic-datatable, #another-basic-datatable, #work-requests-list-datatable, #datatable-closed, #datatable-in-progress, #datatable-draft').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true
            }],
            "paging": false,
            "info": false
        });

        // Special setting for #workrequest-datatable
        $('#workrequest-datatable, #employers-list-datatable, #workers-list-datatable').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true
            }],
            "paging": true,   
            "info": true
        });
    } else {
        console.error("DataTables library is not loaded.");
    }
});

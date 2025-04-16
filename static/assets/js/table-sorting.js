$(document).ready(function () {
    if ($.fn.DataTable) {
        // Tables with common settings
        $('#basic-datatable, #another-basic-datatable, #work-requests-list-datatable, #datatable-closed, #datatable-in-progress, #datatable-draft, #logs-table').DataTable({
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
        $('#workrequest-datatable, #employers-list-datatable').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true
            }],
            "paging": true,   
            "info": true
        });

        $('#recruiters-datatable,#workers-list-datatable').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true
            }],
            "paging": true,   
            "info": true,
            "searching": false
        });
    } else {
        console.error("DataTables library is not loaded.");
    }
});

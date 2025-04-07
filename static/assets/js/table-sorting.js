$(document).ready(function () {
    if ($.fn.DataTable) { 
        $('#basic-datatable, #employers-list-datatable, #workrequest-datatable, #another-basic-datatable, #work-requests-list-datatable').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true 
            }],
            "paging": false,
            "info": false
        });
    } else {
        console.error("DataTables library is not loaded.");
    }
});

$(document).ready(function () {
<<<<<<< HEAD
    $('#basic-datatable, #employers-list-datatable, #workrequest-datatable, #another-basic-datatable, #recruiters-datatable').DataTable({
        "ordering": true,
        "order": [],
        "columnDefs": [{
            "targets": '_all',
            "orderable": true 
        }],
        "paging": false,
        "info": false, 
    });
=======
    if ($.fn.DataTable) { 
        $('#basic-datatable, #employers-list-datatable, #workrequest-datatable, #another-basic-datatable').DataTable({
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
>>>>>>> origin/dev
});

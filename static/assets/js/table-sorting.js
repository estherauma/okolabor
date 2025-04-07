$(document).ready(function () {
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
});

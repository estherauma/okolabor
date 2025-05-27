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
            "paging": true,
            "info": false,

            // "language": {
            //     search: _('dataTableSearch'),
            //     lengthMenu: _('dataTableLengthMenu'),
            //     info: _('dataTableInfo'),
            //     infoEmpty: _('dataTableInfoEmpty'),
            //     infoFiltered: _('dataTableInfoFiltered'),
            //     zeroRecords: _('dataTableZeroRecords'),
            //     emptyTable: _('dataTableEmptyTable'),
            //     paginate: {
            //       first: _('dataTablePaginateFirst'),
            //       last: _('dataTablePaginateLast'),
            //       next: _('dataTablePaginateNext'),
            //       previous: _('dataTablePaginatePrevious')
            //     }

            // }
        });

        // Special setting for #workrequest-datatable
        $('#workrequest-datatable, #employers-list-datatable, #logstable').DataTable({
            "ordering": true,
            "order": [],
            "columnDefs": [{
                "targets": '_all',
                "orderable": true
            }],
            "paging": true,   
            "info": true
        });

         $('#basic-datatable-workers').DataTable({
                "ordering": true,
                "order": [], // No initial ordering
                "columnDefs": [
                    {
                        "targets": '_all', // All other columns
                        "orderable": true
                    }
                ],
                "paging": true,
                "info": true
            });


        // if (!$.fn.DataTable.isDataTable('#logs-table')) {
        //     $('#logs-table').DataTable({
        //         "ordering": true,
        //         "order": [],
        //         "columnDefs": [{
        //             "targets": '_all',
        //             "orderable": true
        //         }],
        //         "paging": true,
        //         "info": true,
                
        //     });
        // }

        
        

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

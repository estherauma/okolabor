document.addEventListener('DOMContentLoaded', function() {
    const columnMap = {
        '1': 'col-name',
        '2': 'col-town',
        '3': 'col-profile',
        '4': 'col-experience',
        '5': 'col-english',
        '6': 'col-location',
        '7': 'col-offer',
        '8': 'col-actions'
    };
    function applyColumnVisibility() {
        document.querySelectorAll('.column-toggle').forEach(function(checkbox) {
            const colIndex = checkbox.value;
            const isVisible = checkbox.checked;
            const columnClass = columnMap[colIndex];

            if (columnClass) {
                document.querySelectorAll(`th.${columnClass}, td.${columnClass}`).forEach(el => {
                    el.style.display = isVisible ? '' : 'none';
                });
            }
        });
    }
    document.getElementById('apply-column-settings').addEventListener('click', function() {
        applyColumnVisibility();
        var modal = bootstrap.Modal.getInstance(document.getElementById('columnSettingsModal'));
        modal.hide();
    });
    document.querySelectorAll('.column-toggle').forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const colIndex = this.value;
            const isVisible = this.checked;
            const columnClass = columnMap[colIndex];

            if (columnClass) {
                document.querySelectorAll(`th.${columnClass}, td.${columnClass}`).forEach(el => {
                    el.style.display = isVisible ? '' : 'none';
                });
            }
        });
    });
    applyColumnVisibility();
});
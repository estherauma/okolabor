document.addEventListener('DOMContentLoaded', function () {
    function initColumnVisibility({
        columnMap,
        storageKey,
        checkboxSelector,
        tableSelector,
        modalId,
        applyButtonId
    }) {
        function applyColumnVisibilityFromStorage() {
            const savedSettings = JSON.parse(localStorage.getItem(storageKey)) || {};

            document.querySelectorAll(checkboxSelector).forEach(function (checkbox) {
                const colIndex = checkbox.value;
                const columnClass = columnMap[colIndex];
                const isVisible = savedSettings[columnClass] !== false;
                checkbox.checked = isVisible;
                if (columnClass) {
                    document.querySelectorAll(`${tableSelector} th.${columnClass}, ${tableSelector} td.${columnClass}`).forEach(el => {
                        if (isVisible) {
                            el.style.display = '';
                            el.classList.remove('is-hidden-column');
                        } else {
                            el.style.display = 'none';
                            el.classList.add('is-hidden-column');
                        }
                    });
                }
            });
        }
        function saveSingleColumnSetting(colIndex, isVisible) {
            const columnClass = columnMap[colIndex];
            const savedSettings = JSON.parse(localStorage.getItem(storageKey)) || {};

            savedSettings[columnClass] = isVisible;
            localStorage.setItem(storageKey, JSON.stringify(savedSettings));
        }
        document.querySelectorAll(checkboxSelector).forEach(function (checkbox) {
            checkbox.addEventListener('change', function () {
                const colIndex = this.value;
                const isVisible = this.checked;
                const columnClass = columnMap[colIndex];
                if (columnClass) {
                    document.querySelectorAll(`${tableSelector} th.${columnClass}, ${tableSelector} td.${columnClass}`).forEach(el => {
                        el.style.display = isVisible ? '' : 'none';
                    });

                    saveSingleColumnSetting(colIndex, isVisible);
                }
            });
        });
        const applyBtn = document.getElementById(applyButtonId);
        if (applyBtn) {
            applyBtn.addEventListener('click', function () {
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                modal?.hide();
            });
        }
        applyColumnVisibilityFromStorage();
    }
    function reapplyColumnVisibility() {
        initColumnVisibility({
            columnMap: {
                '1': 'col-name',
                '2': 'col-town',
                '3': 'col-profile',
                '4': 'col-experience',
                '5': 'col-english',
                '6': 'col-location',
                '7': 'col-offer',
                '8': 'col-actions'
            },
            storageKey: 'tab1ColumnVisibility',
            checkboxSelector: '#columnSettingsModal input.column-toggle',
            tableSelector: '#tab1 table',
            modalId: 'columnSettingsModal',
            applyButtonId: 'apply-column-settings'
        });
        initColumnVisibility({
            columnMap: {
                '1': 'col-name',
                '2': 'col-town',
                '3': 'col-profile',
                '4': 'col-experience',
                '5': 'col-english',
                '6': 'col-location',
                '7': 'col-offer',
                '8': 'col-actions'
            },
            storageKey: 'tab2ColumnVisibility',
            checkboxSelector: '#columnShortListSettingsModal input.column-toggle',
            tableSelector: '#tab2 table',
            modalId: 'columnShortListSettingsModal',
            applyButtonId: 'apply-shortlist-column-settings'
        });
        initColumnVisibility({
            columnMap: {
                '1': 'col-name',
                '2': 'col-town',
                '3': 'col-profile',
                '4': 'col-experience',
                '5': 'col-english',
                '6': 'col-location',
                '7': 'col-offer',
                '8': 'col-actions'
            },
            storageKey: 'tab3ColumnVisibility',
            checkboxSelector: '#columnShortListSettingsModal input.column-toggle',
            tableSelector: '#tab3 table',
            modalId: 'columnShortListSettingsModal',
            applyButtonId: 'apply-shortlist-column-settings'
        });
    }
    initColumnVisibility({
        columnMap: {
            '1': 'col-name',
            '2': 'col-town',
            '3': 'col-profile',
            '4': 'col-experience',
            '5': 'col-english',
            '6': 'col-location',
            '7': 'col-offer',
            '8': 'col-actions'
        },
        storageKey: 'tab1ColumnVisibility',
        checkboxSelector: '#columnSettingsModal input.column-toggle',
        tableSelector: '#tab1 table',
        modalId: 'columnSettingsModal',
        applyButtonId: 'apply-column-settings'
    });
    initColumnVisibility({
        columnMap: {
            '1': 'col-name',
            '2': 'col-town',
            '3': 'col-profile',
            '4': 'col-experience',
            '5': 'col-english',
            '6': 'col-location',
            '7': 'col-offer',
            '8': 'col-actions'
        },
        storageKey: 'tab2ColumnVisibility',
        checkboxSelector: '#columnShortListSettingsModal input.column-toggle',
        tableSelector: '#tab2 table',
        modalId: 'columnShortListSettingsModal',
        applyButtonId: 'apply-shortlist-column-settings'
    });
    initColumnVisibility({
        columnMap: {
            '1': 'col-name',
            '2': 'col-town',
            '3': 'col-profile',
            '4': 'col-experience',
            '5': 'col-english',
            '6': 'col-location',
            '7': 'col-offer',
            '8': 'col-actions'
        },
        storageKey: 'tab3ColumnVisibility',
        checkboxSelector: '#columnShortListSettingsModal input.column-toggle',
        tableSelector: '#tab3 table',
        modalId: 'columnShortListSettingsModal',
        applyButtonId: 'apply-shortlist-column-settings'
    });
    document.addEventListener('click', function(e) {
        if (e.target.matches('.pagination a')) {
            e.preventDefault();
            const url = e.target.getAttribute('href');
            loadNewPage(url, function() {
                reapplyColumnVisibility();
            });
        }
    });
    function loadNewPage(url, callback) {
        setTimeout(function() {
            callback();
        }, 1000);
    }
});

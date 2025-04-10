document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tabs-menu a');
    const allWorkersSettingBtn = document.querySelector('.all-workers-setting-btn');
    const shortlistSettingBtn = document.querySelector('.shortlist-setting-btn');

    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetTab = event.target.getAttribute('href');
            if (targetTab === '#tab1') {
                allWorkersSettingBtn.style.display = 'block';
                shortlistSettingBtn.style.display = 'none';
            } else if (targetTab === '#tab2') {
                allWorkersSettingBtn.style.display = 'none';
                shortlistSettingBtn.style.display = 'block';
            } else {
                allWorkersSettingBtn.style.display = 'none';
                shortlistSettingBtn.style.display = 'none';
            }
        });
    });
});

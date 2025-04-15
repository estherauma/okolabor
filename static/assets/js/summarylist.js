function checkTabFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab') || 'shortlist'; 
    const tabs = ['shortlist', 'offersent', 'confirmed'];

    tabs.forEach(tabName => {
        const tabLink = document.getElementById(`${tabName}-tab`);
        const tabPane = document.getElementById(tabName);
        const tabLi = document.getElementById(`${tabName}-li`);

        if (tabName === tab) {
            // Show only the current tab menu item
            tabLi.style.display = 'list-item';
            tabLink.classList.add('active');
            tabPane.classList.add('active');
            tabPane.style.display = 'block';
        } else {
            // Hide other tab menu items
            tabLi.style.display = 'none';
            tabLink.classList.remove('active');
            tabPane.classList.remove('active');
            tabPane.style.display = 'none';
        }
    });
}

window.onload = checkTabFromURL;
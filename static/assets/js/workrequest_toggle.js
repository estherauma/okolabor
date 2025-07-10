document.addEventListener("DOMContentLoaded", function () {
    const filterSection = document.getElementById("workRequestRoleFilter");
    const tabLinks = document.querySelectorAll(".nav-link");

    function updateFilterVisibility() {
        const activeTab = document.querySelector(".nav-link.active");
        if (activeTab && activeTab.getAttribute("href") === "#tab1") {
            filterSection.style.display = "flex";
        } else {
            filterSection.style.display = "none"; 
        }
    }

    updateFilterVisibility();

    tabLinks.forEach(link => {
        link.addEventListener("shown.bs.tab", updateFilterVisibility);
    });
});
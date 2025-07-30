document.addEventListener("DOMContentLoaded", function() {
    var el = document.getElementById("role-workrequest-data");
    if (el) {
        var workRequestId = el.getAttribute("data-work-request");
        var roleId = el.getAttribute("data-role");
        if (workRequestId) sessionStorage.setItem("selectedWorkRequest", workRequestId);
        if (roleId) sessionStorage.setItem("selectedRole", roleId);
    }
});

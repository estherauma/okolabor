function syncSelectAll(groupClass, selectAllId) {
  const checkboxes = document.querySelectorAll(groupClass);
  const selectAll = document.getElementById(selectAllId);
  checkboxes.forEach(cb => {
    cb.addEventListener("change", () => {
      const allChecked = [...checkboxes].every(c => c.checked);
      selectAll.checked = allChecked;
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  syncSelectAll(".allworkers-checkbox", "select-all-allworkers");
  syncSelectAll(".shortlist-checkbox", "select-all-shortlist");
});

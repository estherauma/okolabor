document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.recruiter-checkbox');
    const assignButton = document.getElementById('assign-button');
    const assignModal = new bootstrap.Modal(document.getElementById('assignModal'));
    const selectedRecruiterName = document.getElementById('selected-recruiter-name');
    const submitButton = document.getElementById('submit-button');
    const assignForm = document.getElementById('assign-form');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
           
            checkboxes.forEach(cb => {
                if (cb !== checkbox) {
                    cb.checked = false;
                }
            });

            assignButton.disabled = !checkbox.checked;
        });
    });

    assignButton.addEventListener('click', function () {
        const selectedCheckbox = document.querySelector('.recruiter-checkbox:checked');
        if (selectedCheckbox) {
            const recruiterId = selectedCheckbox.dataset.recruiterId;
            const recruiterName = selectedCheckbox.closest('tr').querySelector('td:nth-child(2)').textContent;
            selectedRecruiterName.textContent = `${recruiterName}`;
            assignForm.dataset.recruiterId = recruiterId;
            assignModal.show();
        }
    });

    submitButton.addEventListener('click', function () {
        const recruiterId = assignForm.dataset.recruiterId;
        const employerId = document.getElementById('employer-select').value;
        const action = document.getElementById('action-select').value;
        if (action === 'assign') {
            assignForm.action = `/recruiters/add/${employerId}/${recruiterId}/`;
        } else {
            assignForm.action = `/recruiters/remove/${employerId}/${recruiterId}/`;
        }
        assignForm.submit();
    });
});
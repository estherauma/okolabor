function assignRecruiter(recruiterId) {
    let form = document.getElementById(`assign-form-${recruiterId}`);
    let employerId = form.querySelector("select").value;
    form.action = `/recruiters/add/${employerId}/${recruiterId}/`;
    form.submit();
}

function removeRecruiter(recruiterId) {
    let form = document.getElementById(`assign-form-${recruiterId}`);
    let employerId = form.querySelector("select").value;
    form.action = `/recruiters/remove/${employerId}/${recruiterId}/`;
    form.submit();
}

function setupSendMessageModal({
  triggerSelector,
  workRequestSelector,
  roleSelector,
  modalId,
  work_assignment_status,
}) {
  $(triggerSelector).on('click', function (e) {
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();

    if (!workRequestSelected || !roleSelected) {
      e.preventDefault();
      $(modalId).modal('hide');
      alert(
        'Please select a work request and a role before sending a message.'
      );
      return false;
    }
    $.get(
      `/workers/ajax-filtered-workers/?work_request=${workRequestSelected}&role=${roleSelected}&status=${work_assignment_status}`,
      function (response) {
        if (response.workers && response.workers.length > 0) {
          $(modalId).modal('show');
        } else {
          alert('No workers found for the selected role and work request.');
        }
      }
    ).fail(function () {
      alert('Error checking workers. Please try again.');
    });
  });
}
function handleSubmit({
  sendMessageFormSelector,
  workRequestSelector,
  roleSelector,
  work_assignment_status,
}) {
  $(sendMessageFormSelector).on('submit', function (e) {
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();

    // Set hidden inputs
    $(`#id_work_request_${work_assignment_status}`).val(workRequestSelected);
    $(`#id_role_${work_assignment_status}`).val(roleSelected);
    $(`#id_work_assignment_status_${work_assignment_status}`).val(
      work_assignment_status
    );
  });
}

function handleViewMessages({
  workRequestSelector,
  roleSelector,
  work_assignment_status,
}) {
  $(`#view-messages-${work_assignment_status}`).on('click', function (e) {
    e.preventDefault();
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();
    const base = $(this).data('messages-url');
    const params = new URLSearchParams();
    if (!workRequestSelected || !roleSelected) {
      e.preventDefault();
      alert(
        'Please select a work request and a role before sending a message.'
      );
      return;
    }
    params.set('workrequest', workRequestSelected);
    params.set('role', roleSelected);
    params.set('workassignment_status', work_assignment_status);
    window.location.href = `${base}?${params.toString()}`;
  });
}

function handleSendWorkRequestMessage({
  triggerSelector,
  workRequestSelector,
  roleSelector,
  modalId,
  sendMessageFormSelector,
  work_assignment_status,
}) {
  setupSendMessageModal({
    triggerSelector,
    workRequestSelector,
    roleSelector,
    modalId,
    work_assignment_status,
  });
  handleSubmit({
    sendMessageFormSelector,
    workRequestSelector,
    roleSelector,
    work_assignment_status,
  });

  handleViewMessages({
    workRequestSelector,
    roleSelector,
    work_assignment_status,
  })
}

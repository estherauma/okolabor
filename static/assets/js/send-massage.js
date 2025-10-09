function setupSendMessageModal({
  triggerSelector,
  workRequestSelector,
  roleSelector,
  modalId,
}) {
  $(triggerSelector).on('click', function (e) {
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();
    console.log('Work Request Selected:', workRequestSelected);
    console.log('Role Selected:', roleSelected);

    if (!workRequestSelected || !roleSelected) {
      e.preventDefault();
      $(modalId).modal('hide');
      alert(
        'Please select a work request and a role before sending a message.'
      );
      return false;
    }
    // If both are selected, show the modal
    $(modalId).modal('show');
  });
}
function handleSubmit({
  sendMessageFormSelector,
  workRequestSelector,
  roleSelector,
  work_assignment_status,
}) {
  $(sendMessageFormSelector).on('submit', function (e) {
    // Get selected values from your selects
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();

    // Set hidden inputs
    $('#id_work_request').val(workRequestSelected);
    $('#id_role').val(roleSelected);
    $('#id_work_assignment_status').val(work_assignment_status);
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
  });
  handleSubmit({
    sendMessageFormSelector,
    workRequestSelector,
    roleSelector,
    work_assignment_status,
  });
}

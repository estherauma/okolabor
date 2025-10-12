function setupSendMessageModal({
  triggerSelector,
  workRequestSelector,
  roleSelector,
  modalId,
  work_assignment_status
}) {
  $(triggerSelector).on('click', function (e) {
    var workRequestSelected = $(workRequestSelector).val();
    var roleSelected = $(roleSelector).val();
    console.log('Work Request Selected:', workRequestSelected);
    console.log('Role Selected:', roleSelected);

    if (!workRequestSelected || !roleSelected) {
      e.preventDefault();
      $(modalId).modal('hide');
              //translate this
      alert(
        'Please select a work request and a role before sending a message.'
      );
      return false;
    }
    $.get(`/workers/ajax-filtered-workers/?work_request=${workRequestSelected}&role=${roleSelected}&status=${work_assignment_status}`, 
      function(response) {
        console.log('Response from server:', response.workers);
      if (response.workers && response.workers.length > 0) {
        $(modalId).modal('show');
      } else {
        //translate this
        alert('No workers found for the selected role and work request.');
      }
    }).fail(function() {
              //translate this
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
    work_assignment_status
  });
  handleSubmit({
    sendMessageFormSelector,
    workRequestSelector,
    roleSelector,
    work_assignment_status,
  });
}

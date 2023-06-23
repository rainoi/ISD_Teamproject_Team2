
function deleteEmployee(empId) {
  if (confirm('Really want to delete this employee ?')) {
    const form = document.getElementById('deleteForm');
    form.action = form.action.replace('emp_id', empId);
    const confirmDeleteInput = document.createElement('input');
    confirmDeleteInput.type = 'hidden';
    confirmDeleteInput.name = 'confirm_delete';
    confirmDeleteInput.value = 'true';
    form.appendChild(confirmDeleteInput);
    form.submit();
  }
}
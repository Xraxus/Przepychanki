function checkSelected() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
  if (checkboxes.length === 2) {
    // Allow form submission
    return true;
  } else {
    // Prevent form submission
    alert('Zaznacz dokladnie 2 towary!');
    return false;
  }
}
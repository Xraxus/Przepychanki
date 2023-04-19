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

function post_refresh_check(){
    if ( window.history.replaceState ) {

  window.history.replaceState( null, null, window.location.href );

  }
}

function reloadPageWithDelay(delayInMilliseconds) {
  setTimeout(function() {
    window.location.reload(1);
  }, delayInMilliseconds);
}


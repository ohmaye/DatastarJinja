// Datastar configuration
window.datastarConfig = {
  enableUrlHandling: true,
  debug: true,
  logLevel: 'debug'
};

// Initialize debug listeners for Datastar URL handling
document.addEventListener('datastar:ready', function() {
  console.log('Datastar is ready with URL handling enabled');
  
  // Monitor URL replacement attempts
  document.addEventListener('datastar:url-replace', function(e) {
    console.log('URL replacement:', e.detail);
  });
  
  // Monitor fragments received
  document.addEventListener('datastar:fragment-received', function(e) {
    console.log('Fragment received:', e.detail);
    
    // Check for data-replace-url attributes in the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = e.detail.html || '';
    const replaceUrlElements = tempDiv.querySelectorAll('[data-replace-url]');
    
    if (replaceUrlElements.length > 0) {
      console.log('Found data-replace-url elements:', replaceUrlElements);
      replaceUrlElements.forEach(el => {
        console.log('URL to replace with:', el.getAttribute('data-replace-url'));
      });
    }
  });
});
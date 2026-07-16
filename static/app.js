document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.export-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      exportFile(
        btn.getAttribute('data-export-url'),
        btn.getAttribute('data-filename'),
        btn.getAttribute('data-expected-type')
      );
    });
  });
});

function exportFile(url, filename, expectedType) {
  fetch(url, { credentials: 'same-origin' })
    .then(function (response) {
      var contentType = response.headers.get('content-type') || '';
      if (!response.ok || contentType.indexOf(expectedType) === -1) {
        throw new Error('export failed');
      }
      return response.blob();
    })
    .then(function (blob) {
      var objectUrl = URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
      showFlash('Export complete — your file has downloaded.', 'success');
    })
    .catch(function () {
      showFlash('Export failed. Please try again.', 'error');
    });
}

function showFlash(message, category) {
  var container = document.querySelector('.flash-messages');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-messages';
    var main = document.querySelector('main');
    main.parentNode.insertBefore(container, main);
  }
  var p = document.createElement('p');
  p.className = 'flash flash-' + category;
  p.textContent = message;
  container.appendChild(p);
  p.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

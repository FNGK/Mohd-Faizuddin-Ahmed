/* Buttons marked [data-print] open the browser's print dialog. Attached here
   because the site's CSP blocks inline onclick handlers. */
document.querySelectorAll("[data-print]").forEach(function (button) {
  button.addEventListener("click", function () { window.print(); });
});

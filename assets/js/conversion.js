/* Sticky conversion CTA — reveals once the visitor scrolls past the hero.
   Zero dependencies; degrades to always-visible if IO is unavailable.
   The button carries data-dynamic-cta so site.js personalizes its label. */
(function () {
  "use strict";
  var cta = document.querySelector(".sticky-cta");
  if (!cta) return;
  var hero = document.querySelector(".hero");
  if (!("IntersectionObserver" in window) || !hero) {
    cta.classList.add("is-visible");
    return;
  }
  new IntersectionObserver(
    function (entries) {
      cta.classList.toggle("is-visible", !entries[0].isIntersecting);
    },
    { rootMargin: "-45% 0px 0px 0px" }
  ).observe(hero);
})();
